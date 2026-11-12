import { test } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { root } from '../client.mjs';

test('模拟服务验证批量参数、提交记录、下载及重复提交保护', async () => {
  const submitted = [];
  let uploads = 0;
  const server = http.createServer(async (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    if (req.url === '/object_info') return res.end(JSON.stringify({ Test: {} }));
    if (req.url === '/system_stats') return res.end(JSON.stringify({ system: { comfyui_version: 'test' } }));
    if (req.url === '/upload/image') {
      for await (const chunk of req) { /* consume multipart snapshot */ }
      uploads++;
      return res.end(JSON.stringify({ name: 'snapshot.png', subfolder: 'studio' }));
    }
    if (req.url === '/prompt') {
      let body = ''; for await (const chunk of req) body += chunk;
      submitted.push(JSON.parse(body).prompt);
      return res.end(JSON.stringify({ prompt_id: `p${submitted.length}` }));
    }
    if (req.url.startsWith('/history/')) {
      const id = req.url.split('/').at(-1);
      return res.end(JSON.stringify({ [id]: { status: { completed: true, status_str: 'success' }, outputs: { '1': { images: [{ filename: 'test.png', type: 'output', subfolder: '' }] } } } }));
    }
    if (req.url.startsWith('/view?')) return res.end('generated-test-image');
    res.statusCode = 404; res.end('{}');
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const tmp = await fs.mkdtemp(path.join(os.tmpdir(), 'studio-comfy-'));
  const ids = [1, 2].map(n => `comfy-test-${process.pid}-${Date.now()}-${n}`);
  const taskPath = id => path.join(root, 'tasks', 'comfyui', id);
  const legacyTask = path.join(root, 'tasks', ids[0]);
  const asset = `assets/settings/characters/${ids[0]}.png`;
  const assetPath = path.join(root, asset);
  const indexPath = path.join(root, 'platform/comfyui/assets.local.json');
  const previousIndex = await fs.readFile(indexPath).catch(e => { if (e.code === 'ENOENT') return null; throw e; });
  const invoke = (command = 'run', argument = path.join(tmp, 'batch.json')) => new Promise(resolve => {
    const child = spawn(process.execPath, [path.join(root, 'platform/comfyui/client.mjs'), command, argument], { env: { ...process.env, COMFYUI_URL: `http://127.0.0.1:${server.address().port}` } });
    let output = ''; child.stdout.on('data', b => output += b); child.stderr.on('data', b => output += b);
    child.on('close', code => resolve({ code, output }));
  });
  try {
    await fs.writeFile(assetPath, 'test-asset-snapshot');
    await fs.writeFile(path.join(tmp, 'graph.json'), JSON.stringify({ '1': { class_type: 'Test', inputs: { seed: 1, image: '' } } }));
    await fs.writeFile(path.join(tmp, 'definition.json'), JSON.stringify({ bindings: { seed: [{ node: '1', input: 'seed' }], reference: [{ node: '1', input: 'image' }] } }));
    await fs.writeFile(path.join(tmp, 'batch.json'), JSON.stringify({ workflow: 'graph.json', definition: 'definition.json', jobs: ids.map((task, n) => ({ task, parameters: { seed: n + 42, reference: { asset } } })) }));
    const result = await invoke(); assert.equal(result.code, 0, result.output);
    assert.deepEqual(submitted.map(g => g['1'].inputs.seed), [42, 43]);
    assert.equal(uploads, 1);
    assert.equal(submitted[0]['1'].inputs.image, 'studio/snapshot.png');
    assert.equal(await fs.readFile(assetPath, 'utf8'), 'test-asset-snapshot');
    for (const id of ids) {
      assert.equal(await fs.readFile(path.join(taskPath(id), 'output/0-test.png'), 'utf8'), 'generated-test-image');
      const execution = JSON.parse(await fs.readFile(path.join(taskPath(id), 'execution.json'), 'utf8'));
      assert.equal(execution.system.system.comfyui_version, 'test');
      assert.match(execution.assets[asset].sha256, /^[a-f0-9]{64}$/);
    }
    const duplicate = await invoke(); assert.equal(duplicate.code, 1); assert.match(duplicate.output, /任务目录已存在/);
    await fs.rename(taskPath(ids[0]), legacyTask);
    const legacy = await invoke('collect', ids[0]); assert.equal(legacy.code, 0, legacy.output);
    const legacyDuplicate = await invoke(); assert.equal(legacyDuplicate.code, 1); assert.match(legacyDuplicate.output, /任务目录已存在/);
    assert.equal(submitted.length, 2);
  } finally {
    await new Promise(resolve => server.close(resolve));
    for (const id of ids) await fs.rm(taskPath(id), { recursive: true, force: true });
    await fs.rm(legacyTask, { recursive: true, force: true });
    await fs.rm(tmp, { recursive: true, force: true });
    await fs.rm(assetPath, { force: true });
    if (previousIndex) await fs.writeFile(indexPath, previousIndex); else await fs.rm(indexPath, { force: true });
  }
});
