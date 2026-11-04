import fs from 'node:fs/promises';
import path from 'node:path';
import { applyInputs, root } from './client.mjs';

// A definition gives stable names to GUI node inputs; no plugin is installed in ComfyUI.
export function bindParameters(graph, definition = {}, parameters = {}) {
  const overrides = {};
  for (const [name, value] of Object.entries({ ...definition.defaults, ...parameters })) {
    const targets = definition.bindings?.[name];
    if (!Array.isArray(targets) || !targets.length) throw new Error(`未知参数: ${name}`);
    for (const { node, input } of targets) (overrides[node] ||= {})[input] = value;
  }
  return applyInputs(graph, overrides);
}

export async function resolveAssets(value, upload) {
  if (Array.isArray(value)) return Promise.all(value.map(v => resolveAssets(v, upload)));
  if (value && typeof value === 'object') {
    if (Object.hasOwn(value, 'asset')) {
      if (Object.keys(value).length !== 1 || typeof value.asset !== 'string') throw new Error('资产引用应为 {"asset":"assets/..."}');
      const file = path.resolve(root, value.asset);
      const relative = path.relative(await fs.realpath(path.join(root, 'assets')), await fs.realpath(file));
      if (relative.startsWith('..') || path.isAbsolute(relative)) throw new Error('只能引用 assets 内的资产');
      if (!/\.(png|jpg|jpeg|webp)$/i.test(file)) throw new Error('资产上传目前仅支持图片');
      return upload(file);
    }
    const pairs = [];
    for (const [key, item] of Object.entries(value)) pairs.push([key, await resolveAssets(item, upload)]);
    return Object.fromEntries(pairs);
  }
  return value;
}
