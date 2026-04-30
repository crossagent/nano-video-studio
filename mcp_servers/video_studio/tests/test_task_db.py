import pytest
import json

def test_model_registration(temp_db):
    """测试模型注册和配置读取"""
    configs = temp_db.get_all_model_configs()
    assert len(configs) >= 2
    
    # 验证具体内容
    img_model = next(c for c in configs if c['model_id'] == "test_model_image")
    assert img_model['task_type'] == "image"
    assert "size" in img_model['required_params']

def test_task_lifecycle_db(temp_db):
    """测试任务在数据库层面的增删改查"""
    # 1. Add
    tid = temp_db.add_task(
        channel_id="test_channel",
        model_id="test_model_image",
        project="test_proj",
        stage="test_stage",
        prompt="test prompt",
        params={"size": "1024x1024", "extra": "info"}
    )
    assert tid > 0
    
    # 2. Get
    task = temp_db.get_task(tid)
    assert task['prompt'] == "test prompt"
    assert task['params']['size'] == "1024x1024"
    assert task['status'] == 'pending'
    
    # 3. Update
    temp_db.update_task(tid, status='approved')
    task_updated = temp_db.get_task(tid)
    assert task_updated['status'] == 'approved'
    
    # 4. List
    tasks = temp_db.list_tasks(status='approved')
    assert len(tasks) == 1
    assert tasks[0]['id'] == tid
