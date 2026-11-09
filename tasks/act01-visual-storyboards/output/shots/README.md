# 第一幕：白模与视觉首帧候选配对

视频和图像链接指向本机工作文件，Git 保存此清单及逐镜说明。

每个文件夹都包含：`whitebox.mp4`（该镜头白模视频）、`whitebox_first_frame.png`（白模真实起始帧）、`first_frame_candidate.png`（视觉首帧候选）和 `README.md`（帧数、画幅及对齐说明）。

| 镜头 | 内容 | 视频 | 首帧候选 | 白模首帧 |
|---|---|---|---|---|
| 01 | 麦原风暴 | [视频](shot_01/whitebox.mp4) | [候选](shot_01/first_frame_candidate.png) | [白模](shot_01/whitebox_first_frame.png) |
| 02 | 收割机跟拍 | [视频](shot_02/whitebox.mp4) | [候选](shot_02/first_frame_candidate.png) | [白模](shot_02/whitebox_first_frame.png) |
| 03 | 驾驶舱 | [视频](shot_03/whitebox.mp4) | [候选](shot_03/first_frame_candidate.png) | [白模](shot_03/whitebox_first_frame.png) |
| 04 | 防御塔 | [视频](shot_04/whitebox.mp4) | [候选](shot_04/first_frame_candidate.png) | [白模](shot_04/whitebox_first_frame.png) |
| 05 | 板房人物 | [视频](shot_05/whitebox.mp4) | [候选](shot_05/first_frame_candidate.png) | [白模](shot_05/whitebox_first_frame.png) |
| 06 | 地震仪 | [视频](shot_06/whitebox.mp4) | [候选](shot_06/first_frame_candidate.png) | [白模](shot_06/whitebox_first_frame.png) |
| 07 | 板房地震 | [视频](shot_07/whitebox.mp4) | [候选](shot_07/first_frame_candidate.png) | [白模](shot_07/whitebox_first_frame.png) |
| 08 | 刀锋女王 | [视频](shot_08/whitebox.mp4) | [候选](shot_08/first_frame_candidate.png) | [白模](shot_08/whitebox_first_frame.png) |
| 09 | 神庙裂谷 | [视频](shot_09/whitebox.mp4) | [候选](shot_09/first_frame_candidate.png) | [白模](shot_09/whitebox_first_frame.png) |
| 10 | 神庙大门 | [视频](shot_10/whitebox.mp4) | [候选](shot_10/first_frame_candidate.png) | [白模](shot_10/whitebox_first_frame.png) |

**对齐状态**：这是镜头级配对，不代表图像与白模精确配准。视觉候选由五格分镜画面去编号后裁出，画幅约 3.4:1；白模约 2.39:1。08 候选图以原视频第 545 帧为参考，其真正首帧为第 505 帧。尚未测试首帧图和白模视频同时输入生成模型的效果。
