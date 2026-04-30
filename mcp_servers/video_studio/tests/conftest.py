import pytest
import os
import tempfile
from pathlib import Path
import sys

# 将代码目录加入 path
sys.path.append(str(Path(__file__).parent.parent))

from task_db import TaskDB

@pytest.fixture
def temp_db():
    """创建一个临时数据库文件用于测试"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    db = TaskDB(db_path=path)
    
    # 预初始化一些基础模型
    db.register_model(
        channel_id="test_channel",
        model_id="test_model_image",
        task_type="image",
        required_params=["size"]
    )
    db.register_model(
        channel_id="test_channel",
        model_id="test_model_video",
        task_type="video",
        required_params=["duration"]
    )
    
    yield db
    
    # 测试结束后尝试删除临时文件
    try:
        if os.path.exists(path):
            os.remove(path)
    except PermissionError:
        # Windows 上如果连接还没完全释放可能会报错，忽略即可
        pass

@pytest.fixture
def mock_generators(mocker):
    """Mock 掉实际的生成逻辑"""
    mock_img = mocker.patch("gen_image.generate_image", return_value=True)
    mock_vid = mocker.patch("gen_video.generate_video", return_value=True)
    # 模拟文件产生
    mocker.patch("os.path.exists", return_value=True)
    return mock_img, mock_vid
