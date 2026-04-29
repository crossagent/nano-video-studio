import sys
import os
import argparse
from pathlib import Path
from task_db import TaskDB
import gen_image
import gen_video

# 路由配置：表名 -> (Provider, 内部模型名称)
MODEL_ROUTES = {
    "model_openrouter_gpt54_image": ("openrouter", "openai/gpt-5.4-image-2"),
    "model_volcengine_seedream_image": ("volcengine", "doubao-seedream-5-0-260128"),
    "model_volcengine_seedance_video": ("volcengine", "doubao-seedance-2-0-fast-260128")
}

def execute_task(table_name, task_id):
    db = TaskDB()
    task = db.get_task(table_name, task_id)
    
    if not task:
        print(f"Error: Task {task_id} not found in {table_name}.")
        return

    if task['status'] == 'completed':
        print(f"Task {task_id} already completed.")
        return

    print(f"Starting Task {task_id} from {table_name}...")
    db.update_task(table_name, task_id, status='executing')

    provider, model_name = MODEL_ROUTES.get(table_name, (None, None))
    if not provider:
        print(f"Error: No route defined for table {table_name}.")
        db.update_task(table_name, task_id, status='failed', error_msg="Unknown model table route.")
        return

    # 生成输出路径：[项目名]/assets/[阶段]/output/
    project_name = task.get('project', 'default')
    output_dir = Path(f"{project_name}/assets/{task['stage']}/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    ext = ".mp4" if "video" in table_name else ".png"
    output_path = str(output_dir / f"{table_name}_{task_id}{ext}")

    try:
        # 解析参考资产 (JSON 格式)
        ref_assets = []
        if task.get('ref_images_json'):
            try:
                ref_assets = json.loads(task['ref_images_json'])
            except:
                print("Warning: Failed to parse ref_images_json.")

        success = False
        if "video" in table_name:
            # 视频生成逻辑
            # 视频模型目前主要关注第一张图作为关键帧参考
            images_ref = [a['path'] for a in ref_assets if a.get('path')]
            success = gen_video.generate_video(
                prompt=task['prompt'],
                output_path=output_path,
                images=images_ref
            )
        else:
            # 图像生成逻辑
            # 传入结构化的 ref_assets 到 gen_image
            gen_image.generate_image(
                prompt=task['prompt'],
                output_path=output_path,
                model=model_name,
                size=task.get('size'),
                aspect_ratio=task.get('aspect_ratio'),
                ref_assets=ref_assets
            )
            success = os.path.exists(output_path)

        if success:
            print(f"Task {task_id} successful: {output_path}")
            # 这里可以增加成本计算逻辑，目前先填固定占位
            cost_str = "0.1 CNY" if provider == "volcengine" else "0.05 USD"
            db.update_task(table_name, task_id, status='completed', output_path=output_path, cost_info=cost_str)
        else:
            print(f"Task {task_id} failed.")
            db.update_task(table_name, task_id, status='failed', error_msg="Generation script returned False or no file.")

    except Exception as e:
        print(f"Exception during Task {task_id}: {str(e)}")
        db.update_task(table_name, task_id, status='failed', error_msg=str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Task Runner: Executing tasks from model tables.")
    parser.add_argument("--table", required=True, help="Model table name")
    parser.add_argument("--id", type=int, required=True, help="Task ID")
    
    args = parser.parse_args()
    execute_task(args.table, args.id)
