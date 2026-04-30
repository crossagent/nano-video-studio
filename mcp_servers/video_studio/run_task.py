import os
import json
from pathlib import Path
from task_db import TaskDB
import gen_image
import gen_video

from dotenv import load_dotenv

# 获取项目根目录并加载环境变量
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# 优先级：.env 中的 STUDIO_WORKSPACE > 默认根目录
WORKSPACE = Path(os.getenv("STUDIO_WORKSPACE", str(ROOT_DIR)))

# 渠道映射配置 (Channel -> Provider)
CHANNEL_TO_PROVIDER = {
    "volcengine": "volcengine",
    "openrouter": "openrouter"
}

def execute_task(task_id):
    db = TaskDB()
    task = db.get_task(task_id)
    
    if not task:
        return False, f"Error: Task {task_id} not found."

    if task['status'] == 'completed':
        return True, f"Task {task_id} already completed."

    # 更新为执行中
    db.update_task(task_id, status='executing')

    # 获取渠道和模型信息
    channel = task['channel_id']
    model_id = task['model_id']
    provider = CHANNEL_TO_PROVIDER.get(channel)
    
    # 确定任务类型
    is_video = "video" in model_id.lower() or "seedance" in model_id.lower()

    # 生成输出路径
    project_name = task.get('project', 'default')
    output_dir = WORKSPACE / project_name / "assets" / task['stage'] / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ext = ".mp4" if is_video else ".png"
    output_path = str(output_dir / f"task_{task_id}_{model_id.replace('/', '_')}{ext}")

    try:
        # 获取模型特定参数
        params = task.get('params', {})
        
        # 处理参考资产
        ref_assets = []
        if 'ref_images_json' in params:
            try:
                ref_val = params['ref_images_json']
                ref_assets = json.loads(ref_val) if isinstance(ref_val, str) else ref_val
            except:
                pass

        success = False
        if is_video:
            # 视频生成逻辑
            images_ref = [a['path'] for a in ref_assets if isinstance(a, dict) and a.get('path')]
            success = gen_video.generate_video(
                prompt=task['prompt'],
                output_path=output_path,
                images=images_ref,
                **{k: v for k, v in params.items() if k != 'ref_images_json'}
            )
        else:
            # 图像生成逻辑
            success = gen_image.generate_image(
                prompt=task['prompt'],
                output_path=output_path,
                model=model_id,
                ref_assets=ref_assets,
                **{k: v for k, v in params.items() if k != 'ref_images_json'}
            )
            if not success: 
                success = os.path.exists(output_path)

        if success:
            cost_str = "0.1 CNY" if provider == "volcengine" else "0.05 USD"
            db.update_task(task_id, status='completed', output_path=output_path, cost_info=cost_str)
            return True, f"Task {task_id} successful: {output_path}"
        else:
            db.update_task(task_id, status='failed', error_msg="Generation failed.")
            return False, f"Task {task_id} failed."

    except Exception as e:
        db.update_task(task_id, status='failed', error_msg=str(e))
        return False, f"Exception: {str(e)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()
    execute_task(args.id)
