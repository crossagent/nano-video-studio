import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';

const root = process.cwd();
const task = 'tasks/scene-reference-sotx-002';
const asset = 'assets/settings/scenes';
const rows = JSON.parse(await fs.readFile(`${task}/selected-sources.json`, 'utf8'));
const records = [];
for (const row of rows) {
  const bytes = await fs.readFile(row.source);
  if (bytes.subarray(0,8).toString('hex') !== '89504e470d0a1a0a') throw Error(`Not PNG: ${row.id}`);
  const width = bytes.readUInt32BE(16), height = bytes.readUInt32BE(20);
  const chunks = [];
  let i = 8, ended = false;
  while (i < bytes.length) {
    const len = bytes.readUInt32BE(i), type = bytes.toString('ascii', i+4, i+8);
    if (type === 'IDAT') chunks.push(bytes.subarray(i+8,i+8+len));
    if (type === 'IEND') ended = true;
    i += len + 12;
  }
  if (!ended || !chunks.length) throw Error(`Incomplete PNG: ${row.id}`);
  const decoded = zlib.inflateSync(Buffer.concat(chunks));
  if (!decoded.length) throw Error(`Empty PNG: ${row.id}`);
  const output = `${task}/output/${row.id}-v2.png`;
  const target = `${asset}/${row.id}.png`;
  await fs.copyFile(row.source, output);
  try { await fs.access(target); throw Error(`Asset already exists: ${target}`); } catch(e) { if(e.code !== 'ENOENT') throw e; }
  await fs.copyFile(output,target);
  let spec = await fs.readFile(`${asset}/${row.id}.md`,'utf8');
  spec = spec.replaceAll(`${row.id}.jpg`,`${row.id}.png`);
  spec += `\n\n## 参考图交付 v2（2026-11-04）\n\n![${row.title}](${row.id}.png)\n\n- 图片：${width}×${height} PNG，接近16:9，保留工具原始画幅。\n- 来源任务：\`${task}\`；生成方式：内置 image_gen；完整提示词与参考来源见任务档案。模型版本与seed未公开。\n- 本版视觉基准：遵循用户修订后的导弹塔图，低对比度、柔和高光、可读中间调、克制反射与真实材质；此项优先于早期规格中高反差、强光及镜面效果描述。\n- 构图与空间、材质、光源按上述设定用于分镜参考；属于项目概念设计，并非官方游戏原画或测量施工图。\n- 关联：\`assets/storyboards/act-01-storyboard-script.md\`、本场景原有规格。\n`;
  if (row.id.startsWith('scene-02')) spec += '\n- 导弹塔形制以任务 inputs 中游戏外观参考为准：矮壮装甲支撑基座，中央传感器，左右两组上下叠置圆形发射口；废止旧版高钢架与巨大雷达盘的通用防空塔描述。\n';
  await fs.writeFile(`${asset}/${row.id}.md`,spec,'utf8');
  records.push({...row,output,target,width,height,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),verification:'PNG chunks and decompression valid; visual review in chat',version:'v2'});
}
await fs.writeFile(`${task}/outputs.json`,JSON.stringify(records,null,2)+'\n');
let readme = await fs.readFile(`${asset}/README.md`,'utf8');
for(const r of records) {
  readme=readme.replaceAll(`\`${r.id}.jpg\``,`[查看参考图](${r.id}.png)`);
  readme=readme.replaceAll(`file:///D:/nano-video-studio/${asset}/${r.id}.md`,`${r.id}.md`);
}
readme += '\n\n## 2026-11-04 参考图更新\n\n七张参考图已按修订后的低对比度写实风格重绘，实际原图均为PNG。导弹塔形制参照StarCraft II游戏造型。来源任务：`tasks/scene-reference-sotx-002`；完整参数与提示词见该任务。\n\n';
for(const r of records) readme += `### ${r.title}\n\n![${r.title}](${r.id}.png)\n\n`;
await fs.writeFile(`${asset}/README.md`,readme,'utf8');
let tm=await fs.readFile(`${task}/task.md`,'utf8');
await fs.writeFile(`${task}/task.md`,tm.replace('状态：running','状态：completed'));
await fs.appendFile(`${task}/log.md`,'\n- 用户进一步要求以修订导弹塔风格和星际设定重绘其他场景，已完成其余六张v2。\n- 七张v1仅保留于任务output，未入正式资产；七张v2经逐图检查后复制入assets/settings/scenes，与设定/场景设定目录联接同步可见。\n- PNG签名、文件块、像素尺寸及压缩流解码检查通过；提示词、源路径、SHA-256和资产路径保存在outputs.json。\n- 实际1672×941原图，未声称2048×1152，未做拉伸或锐化。\n- 本批为场景设计概念参考，空间尺度与角色表演连续性需后续分镜/搭建时具体确定。\n');
console.log(records.map(r=>({id:r.id,width:r.width,height:r.height,target:r.target})));
