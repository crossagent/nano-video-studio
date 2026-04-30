import pytest
import sys
from pathlib import Path

# Mock TaskDB to use the temp_db fixture
import server
import run_task

def test_validate_params(mocker, temp_db):
    """测试参数校验逻辑"""
    # 让 server 使用我们的测试数据库
    mocker.patch("server.TaskDB", return_value=temp_db)
    
    # 1. 成功案例
    ok, err = server._validate("test_channel", "test_model_image", "image", {"size": "1024"})
    assert ok is True
    
    # 2. 缺少参数
    ok, err = server._validate("test_channel", "test_model_image", "image", {})
    assert ok is False
    assert "Missing params" in err
    
    # 3. 类型错误 (用图像模型发视频请求)
    ok, err = server._validate("test_channel", "test_model_image", "video", {"duration": 5})
    assert ok is False
    assert "is for image, not video" in err

def test_submit_flow(mocker, temp_db):
    """测试提交任务的工具函数"""
    mocker.patch("server.TaskDB", return_value=temp_db)
    
    # 提交图像任务
    res = server.submit_image_task(
        "test_channel", "test_model_image", "proj", "stage", "prompt", {"size": "1024"}
    )
    assert "submitted successfully" in res
    
    # 验证数据库里确实有了
    tasks = temp_db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]['model_id'] == "test_model_image"

def test_execution_logic(mocker, temp_db, mock_generators):
    """测试执行逻辑的控制流"""
    mocker.patch("run_task.TaskDB", return_value=temp_db)
    mock_img, mock_vid = mock_generators
    
    # 1. 准备一个已审批的任务
    tid = temp_db.add_task("test_channel", "test_model_image", "p", "s", "prompt", {"size": "1024"})
    temp_db.update_task(tid, status='approved')
    
    # 2. 执行
    success, msg = run_task.execute_task(tid)
    
    assert success is True
    assert "successful" in msg
    # 验证是否真的调用了 gen_image (而不是 gen_video)
    mock_img.assert_called_once()
    mock_vid.assert_not_called()
    
    # 验证数据库状态更新
    task = temp_db.get_task(tid)
    assert task['status'] == 'completed'
    assert task['output_path'] is not None
