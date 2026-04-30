import requests
import json
import base64
import os
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 获取本地 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

def encode_image(image_path):
    """将本地图片转为 Base64 Data URI"""
    mime_type = "image/png"
    if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg"):
        mime_type = "image/jpeg"
    
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"

def submit_task(prompt, images=None, videos=None, audios=None):
    """提交视频生成任务"""
    api_key = os.getenv("ARK_API_KEY")
    model = os.getenv("VIDEO_MODEL", "doubao-seedance-2-0-fast-260128")
    
    if not api_key:
        print("错误: 未找到 ARK_API_KEY 环境变量")
        return None

    url = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    content = [{"type": "text", "text": prompt}]
    
    if images:
        for img in images:
            if os.path.exists(img):
                img_data = encode_image(img)
            else:
                img_data = img # 假设是 URL
            
            content.append({
                "type": "image_url",
                "image_url": {"url": img_data},
                "role": "reference_image"
            })

    if videos:
        for vid in videos:
            content.append({
                "type": "video_url",
                "video_url": {"url": vid},
                "role": "reference_video"
            })

    if audios:
        for aud in audios:
            content.append({
                "type": "audio_url",
                "audio_url": {"url": aud},
                "role": "reference_audio"
            })

    payload = {
        "model": model,
        "content": content,
        "generate_audio": True,
        "ratio": os.getenv("VIDEO_RATIO", "16:9"),
        "duration": int(os.getenv("VIDEO_DURATION", "5")),
        "watermark": False
    }

    print(f"正在提交任务到 {model}...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"收到响应: {response.status_code}")
        if response.status_code != 200:
            print(f"提交任务失败 ({response.status_code}): {response.text}")
            return None
        
        result = response.json()
        task_id = result.get("id")
        print(f"任务已提交，ID: {task_id}")
        return task_id
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None

def poll_task(task_id, timeout=300, interval=10):
    """轮询任务状态"""
    api_key = os.getenv("ARK_API_KEY")
    url = f"https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"查询任务失败 ({response.status_code}): {response.text}")
                return None
            
            result = response.json()
            status = result.get("status")
            print(f"当前状态: {status}")

            if status == "succeeded":
                # 检查结果中的视频 URL
                video_url = result.get("content", {}).get("video_url")
                if not video_url:
                    # 备选路径，防止不同版本 API 差异
                    video_url = result.get("output", {}).get("video_url")
                return video_url
            elif status == "failed":
                print(f"任务失败: {result.get('error')}")
                return None
            
        except Exception as e:
            print(f"轮询异常: {str(e)}")
        
        time.sleep(interval)
    
    print("任务超时")
    return None

def download_video(url, output_path):
    """下载生成的视频"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"视频已下载至: {output_path}")
        return True
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return False

def generate_video(prompt, output_path, images=None, videos=None, audios=None):
    """完整视频生成流程"""
    task_id = submit_task(prompt, images, videos, audios)
    if not task_id:
        return False
    
    video_url = poll_task(task_id)
    if video_url:
        return download_video(video_url, output_path)
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Volcengine Ark 视频生成工具")
    parser.add_argument("--prompt", required=True, help="生成描述文字")
    parser.add_argument("--output", required=True, help="输出视频路径")
    parser.add_argument("--images", nargs='*', help="参考图片路径或 URL")
    parser.add_argument("--videos", nargs='*', help="参考视频 URL")
    parser.add_argument("--audios", nargs='*', help="参考音频 URL")
    
    args = parser.parse_args()
    
    generate_video(args.prompt, args.output, args.images, args.videos, args.audios)
