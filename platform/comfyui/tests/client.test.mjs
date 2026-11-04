import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyInputs } from '../client.mjs';
import { bindParameters, resolveAssets } from '../workflows.mjs';
test('API 覆盖参数不会修改原工作流，保留节点连线', () => {
  const graph = { '1': { class_type: 'KSampler', inputs: { seed: 1, model: ['2', 0] } } };
  const patched = applyInputs(graph, { '1': { seed: 42 } });
  assert.equal(patched['1'].inputs.seed, 42);
  assert.equal(graph['1'].inputs.seed, 1);
  assert.deepEqual(patched['1'].inputs.model, ['2', 0]);
});

test('命名参数可绑定多个节点且拒绝未声明参数', () => {
  const graph = { '1': { class_type: 'Test', inputs: { seed: 1 } }, '2': { class_type: 'Test', inputs: { seed: 2 } } };
  const definition = { bindings: { seed: [{ node: '1', input: 'seed' }, { node: '2', input: 'seed' }] }, defaults: { seed: 4 } };
  const result = bindParameters(graph, definition, { seed: 42 });
  assert.equal(result['1'].inputs.seed, 42);
  assert.equal(result['2'].inputs.seed, 42);
  assert.equal(graph['1'].inputs.seed, 1);
  assert.throws(() => bindParameters(graph, definition, { typo: 1 }), /未知参数/);
});

test('资产引用不能访问工程资产以外文件', async () => {
  await assert.rejects(resolveAssets({ asset: 'README.md' }, () => assert.fail('不应上传')), /只能引用 assets/);
  assert.deepEqual(await resolveAssets({ seed: 1, model: ['2', 0] }, () => assert.fail()), { seed: 1, model: ['2', 0] });
});
test('拒绝 UI 格式和不存在的节点输入', () => {
  assert.throws(() => applyInputs({ nodes: [] }), /API/);
  const graph = { '1': { class_type: 'Test', inputs: { seed: 1 } } };
  assert.throws(() => applyInputs(graph, { '2': { seed: 1 } }), /节点不存在/);
  assert.throws(() => applyInputs(graph, { '1': { typo: 1 } }), /输入不存在/);
});
