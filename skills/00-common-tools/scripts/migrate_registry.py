from task_db import TaskDB
import os

def migrate():
    # 如果存在旧数据库，为了测试方便我们可以删掉它重新开始（或者你也可以手动删）
    # os.remove("generation_tasks.db") 
    
    db = TaskDB()
    
    # 注册模型（现在不需要 table_name 和 extra_columns 了，只需要必填参数）
    db.register_model(
        channel_id="openrouter",
        model_id="openai/gpt-5.4-image-2",
        task_type="image",
        required_params=["size", "aspect_ratio"]
    )

    db.register_model(
        channel_id="volcengine",
        model_id="doubao-seedream-5-0-260128",
        task_type="image",
        required_params=["size"]
    )

    db.register_model(
        channel_id="volcengine",
        model_id="doubao-seedance-2-0-fast-260128",
        task_type="video",
        required_params=["duration", "aspect_ratio"]
    )
    
    print("New Big-Table Registry Initialized.")

if __name__ == "__main__":
    migrate()
