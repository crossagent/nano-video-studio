---
name: "07-video-production"
description: "负责视频的最终合成、渲染与音画同步。当需要拼接素材、对齐音频、添加特效并输出最终视频文件时调用。触发词：'合成视频'、'视频渲染'、'音画同步'。"
---

# 视频合成 (Video Production)

## 1. 技能描述
本技能负责将所有前期生成的资产进行最终的缝合与渲染。

## 2. 使用时机
- 当所有分镜对应的视频素材生成完毕后。

## 3. 执行指令
1. **素材校验**：检查分辨率、帧率。
2. **视频生成任务流 (Video Generation Workflow)**：
   - **创建提案 (Propose)**：
     使用 `video-studio` MCP 服务的 `submit_video_task` 工具添加任务。必须关联对应的分镜关键帧。
   - **获取审批**：向用户展示视频生成参数、成本及关联分镜图，等待批准。
   - **触发执行 (Execute)**：
     通过 `video-studio` MCP 服务的 `approve_task` 和 `execute_task` 启动生成任务。
3. **音画对齐 (Syncing)**：精确对齐音频与画面。
4. **后期处理**：添加转场、调色、字幕。

## 4. 交付物与存放位置
- **最终视频文件**: `[project]/assets/07-production/output/final_video.mp4`
- **项目元数据 (JSON)**: `[project]/assets/07-production/output/project_metadata.json`
- **封面图**: `[project]/assets/07-production/output/cover.jpg`

## 5. 约束与规范
- 默认输出 1080p, 30fps, H.264 编码。
- 交付物必须严格存放在 `[project]/assets/07-production/output/` 目录下。

## 6. 示例
```json
{
  "project_name": "未来城市",
  "total_duration": 60,
  "output_file": "[project]/assets/07-production/output/final_video.mp4"
}
```
