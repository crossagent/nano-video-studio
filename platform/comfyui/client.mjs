import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { bindParameters, resolveAssets } from './workflows.mjs';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const tasksRoot = path.join(root, 'tasks');
const comfyTasks = path.join(tasksRoot, 'comfyui');
const base = (process.env.COMFYUI_URL || 'http://127.0.0.1:8188').replace(/\/$/, '');
export async function request(route, options = {}) {
  const response = await fetch(base + route, { ...options, signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`ComfyUI ${response.status}: ${await response.text()}`);
  return response;
}
export function applyInputs(graph, overrides = {}) {
  const result = structuredClone(graph);
  if (!result || Array.isArray(result) || typeof result !== 'object' || !Object.keys(result).length || Object.values(result).some(n => !n.class_type || !n.inputs)) {
    throw new Error('需要 ComfyUI API 格式的节点图，不能使用界面工作流 JSON');
  }
  for (const [id, values] of Object.entries(overrides)) {
    if (!result[id]) throw new Error(`节点不存在: ${id}`);
    for (const [key, value] of Object.entries(values)) {
      if (!Object.hasOwn(result[id].inputs, key)) throw new Error(`输入不存在: ${id}.${key}`);
      result[id].inputs[key] = value;
    }
  }
  return result;
}
function taskDirectory(id) {
  if (!/^[a-zA-Z0-9][a-zA-Z0-9_-]*$/.test(id)) throw new Error('无效任务 ID');
  return path.join(comfyTasks, id);
}
async function directoryExists(dir) {
  try {
    await fs.access(dir);
    return true;
  } catch (error) {
    if (error.code === 'ENOENT') return false;
    throw error;
  }
}
async function json(file) { return JSON.parse((await fs.readFile(file, 'utf8')).replace(/^\uFEFF/, '')); }
async function save(file, value) { await fs.writeFile(file, JSON.stringify(value, null, 2) + '\n'); }
async function uploadAsset(file) {
  const relative = path.relative(root, file).replaceAll('\\', '/');
  const data = await fs.readFile(file);
  const hash = createHash('sha256').update(relative).update(data).digest('hex').slice(0, 20);
  const form = new FormData();
  form.set('image', new Blob([data]), `studio-${hash}${path.extname(file).toLowerCase()}`);
  form.set('type', 'input');
  form.set('overwrite', 'false');
  const uploaded = await (await request('/upload/image', { method: 'POST', body: form })).json();
  return { image: uploaded.subfolder ? `${uploaded.subfolder}/${uploaded.name}` : uploaded.name, sha256: createHash('sha256').update(data).digest('hex') };
}
export async function syncAssets() {
  const index = {};
  async function walk(dir) {
    for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
      const file = path.join(dir, entry.name);
      if (entry.isDirectory()) await walk(file);
      else if (entry.isFile() && /\.(png|jpg|jpeg|webp)$/i.test(entry.name)) {
        const relative = path.relative(root, file).replaceAll('\\', '/');
        index[relative] = await uploadAsset(file);
      }
    }
  }
  await walk(path.join(root, 'assets'));
  await save(path.join(root, 'platform/comfyui/assets.local.json'), index);
  return index;
}
export async function submit(manifestFile) {
  const manifestPath = path.resolve(manifestFile);
  const manifest = await json(manifestPath);
  const workflow = await json(path.resolve(path.dirname(manifestPath), manifest.workflow));
  const definition = manifest.definition ? await json(path.resolve(path.dirname(manifestPath), manifest.definition)) : {};
  const jobs = manifest.jobs;
  if (!Array.isArray(jobs) || !jobs.length) throw new Error('jobs 不能为空');
  const seen = new Set();
  const prepared = jobs.map(job => {
    const dir = taskDirectory(job.task);
    if (seen.has(job.task)) throw new Error(`重复任务: ${job.task}`);
    seen.add(job.task);
    return { job, dir, graph: applyInputs(bindParameters(workflow, definition, job.parameters), job.inputs) };
  });
  // 批次全量预检；存在任务目录时拒绝重复提交。
  for (const item of prepared) {
    if (await directoryExists(item.dir) || await directoryExists(path.join(tasksRoot, item.job.task))) {
      throw new Error(`任务目录已存在: ${item.job.task}，请检查原执行记录`);
    }
  }
  const nodeTypes = await (await request('/object_info')).json();
  for (const { graph } of prepared) {
    for (const node of Object.values(graph)) {
      if (!nodeTypes[node.class_type]) throw new Error(`ComfyUI 缺少节点: ${node.class_type}`);
    }
  }
  const uploaded = {};
  // Resolve every local reference before submitting the first GPU job.
  for (const item of prepared) {
    item.assets = {};
    item.graph = await resolveAssets(item.graph, async file => {
      const key = path.relative(root, file).replaceAll('\\', '/');
      uploaded[key] ||= await uploadAsset(file);
      item.assets[key] = uploaded[key];
      return uploaded[key].image;
    });
  }
  const system = await (await request('/system_stats')).json();
  await fs.mkdir(comfyTasks, { recursive: true });
  for (const { job, dir, graph, assets } of prepared) {
    await fs.mkdir(dir);
    await fs.mkdir(path.join(dir, 'output'));
    await fs.writeFile(path.join(dir, 'task.md'), `# ${job.task}\n\n- 平台：ComfyUI\n- 要求：${job.requirements || '见 workflow.json 与 inputs.json'}\n- 状态：planned\n- 验收：${job.acceptance || '待按任务要求评审'}\n`);
    await fs.writeFile(path.join(dir, 'workflow.md'), '# 执行流程\n\n提交 workflow.json 到 POST /prompt，按 prompt_id 查询历史，下载输出到 output/，验收后再归入 assets。\n');
    await save(path.join(dir, 'workflow.json'), graph);
    await save(path.join(dir, 'inputs.json'), job);
    await save(path.join(dir, 'execution.json'), { endpoint: base, assets, definition, system });
    // 先记录提交意图；连接断开时不要自动重试，避免重复占用 GPU。
    await fs.writeFile(path.join(dir, 'log.md'), '# 执行记录\n\n准备提交；若缺少 prompt_id，请检查 ComfyUI 队列后再决定是否重建任务。\n');
    const response = await (await request('/prompt', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: graph }) })).json();
    await save(path.join(dir, 'submission.json'), response);
    if (!response.prompt_id) throw new Error(JSON.stringify(response));
    await fs.appendFile(path.join(dir, 'log.md'), `\n已提交：${response.prompt_id}\n`);
    console.log(`${job.task}: ${response.prompt_id}`);
  }
}
export async function collect(id) {
  const standardDir = taskDirectory(id);
  const legacyDir = path.join(tasksRoot, id);
  const useLegacy = !(await directoryExists(standardDir)) && await directoryExists(legacyDir);
  const dir = useLegacy ? legacyDir : standardDir;
  const execution = await json(path.join(dir, 'execution.json')).catch(error => {
    if (error.code === 'ENOENT') return {};
    throw error;
  });
  if (execution.endpoint && execution.endpoint !== base) throw new Error(`任务提交到 ${execution.endpoint}，请使用同一 COMFYUI_URL 收集`);
  const { prompt_id } = await json(path.join(dir, 'submission.json'));
  if (!prompt_id) throw new Error('缺少 prompt_id');
  const history = await (await request(`/history/${encodeURIComponent(prompt_id)}`)).json();
  const item = history[prompt_id];
  if (!item) { console.log('尚在排队或执行中；稍后再次 collect'); return false; }
  await save(path.join(dir, 'history.json'), item);
  if (item.status?.status_str === 'error') throw new Error(`执行失败，详见 ${dir}/history.json`);
  if (!item.status?.completed) { console.log('尚未完成'); return false; }
  const outputs = [];
  for (const [node, values] of Object.entries(item.outputs || {})) {
    for (const list of Object.values(values)) {
      if (!Array.isArray(list)) continue;
      for (const file of list) {
        if (!file || typeof file.filename !== 'string' || file.type !== 'output') continue;
        const query = new URLSearchParams({ filename: file.filename, subfolder: file.subfolder || '', type: file.type });
        const response = await request(`/view?${query}`);
        const local = `${outputs.length}-${path.basename(file.filename)}`;
        await fs.writeFile(path.join(dir, 'output', local), Buffer.from(await response.arrayBuffer()));
        outputs.push({ node, remote: file, local: `output/${local}` });
      }
    }
  }
  await save(path.join(dir, 'outputs.json'), outputs);
  await fs.appendFile(path.join(dir, 'log.md'), `\n执行完成，已收集 ${outputs.length} 个输出；等待验收。\n`);
  console.log(`${id}: ${outputs.length} 个输出。自定义节点若未在历史返回文件描述，请检查 history.json。`);
  return true;
}
export async function runBatch(file) {
  await submit(file);
  const manifest = await json(path.resolve(file));
  const pending = new Set(manifest.jobs.map(job => job.task));
  const failures = [];
  const deadline = Date.now() + (manifest.timeoutSeconds ?? 21600) * 1000;
  while (pending.size) {
    for (const id of pending) {
      try { if (await collect(id)) pending.delete(id); }
      catch (error) { failures.push(`${id}: ${error.message}`); pending.delete(id); }
    }
    if (!pending.size) break;
    if (Date.now() >= deadline) throw new Error(`等待超时，任务仍在服务端运行，可用 collect 继续收集: ${[...pending].join(', ')}`);
    await new Promise(resolve => setTimeout(resolve, 3000));
  }
  if (failures.length) throw new Error(failures.join('\n'));
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [command, argument] = process.argv.slice(2);
  try {
    if (command === 'status') console.log(await (await request('/system_stats')).json());
    else if (command === 'sync-assets') console.log(await syncAssets());
    else if (command === 'submit' && argument) await submit(argument);
    else if (command === 'run' && argument) await runBatch(argument);
    else if (command === 'collect' && argument) await collect(argument);
    else throw new Error('用法: node platform/comfyui/client.mjs status|sync-assets|submit <批次.json>|run <批次.json>|collect <task-id>');
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
