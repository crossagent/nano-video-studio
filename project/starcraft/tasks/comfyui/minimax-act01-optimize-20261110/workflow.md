# 操作与依据

从 `platform/comfyui/workflows/starcraft-act01-previs-to-video.api.json` 复制任务专用图。单镜输入 90 帧、24 fps、1920×804。输出 608×256、90 帧，20 步、无加速 LoRA。为适配模型 17n+5 帧数规则，在原 84 帧末尾重复 6 帧。

来源：

- [Mickmumpitz 的白模渲染教程与工作流](https://mickmumpitz.ai/posts/new-video-free-166463119?l=en-GB) 建议视频提供构图、运动和时间，外观图提供材质与光照，提示覆盖整个片段，并说明 20 步不加速配置。
- [ComfyUI MiniMax H3 文档](https://github.com/Comfy-Org/docs/blob/main/tutorials/video/minimax/minimax-h3-native.mdx) 指出视频输入按 24 fps 处理，需明确参考作用，强调参考一致性时建议 20–25 步。
- [MiniMax 官方参考模式提示指南](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/VIDEO_PROMPT_WRITING_GUIDE_ref_en.md) 描述 reference generation 中视频用作镜头和时间结构、图片用作主体与场景参考的表达方式。

这次改变片段时长、外观图、提示词与采样步数，因此结果用于验证改进方案，无法单独归因于其中某一变量。
