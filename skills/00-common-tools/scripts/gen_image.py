import requests
import json
import base64
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def encode_image(image_path):
    """将本地图片转为 Base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_base64_image(base64_data, output_path):
    """将 Base64 数据保存为本地图片"""
    # 处理可能的 data:image/png;base64, 前缀
    if "," in base64_data:
        base64_data = base64_data.split(",")[1]
    
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(base64_data))
    print(f"图片已保存至: {output_path}")

def generate_image(prompt, output_path, base_image_path=None, api_key=None):
    """调用 OpenRouter API 使用 openai/gpt-5.4-image-2 生成或迭代图片"""
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
    
    if api_key:
        api_key = api_key.strip()
    
    if not api_key:
        print("错误: 未找到 OPENROUTER_API_KEY 环境变量")
        return
    
    # 调试信息：检查 API Key 是否正确加载（仅显示前几位和长度）
    print(f"DEBUG: API Key loaded, length: {len(api_key)}, starts with: {api_key[:10]}...")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/trae-ide", # 推荐添加
        "X-Title": "Nano Video Studio",               # 推荐添加
    }

    # 构建消息内容
    user_content = [{"type": "text", "text": prompt}]
    
    if base_image_path and os.path.exists(base_image_path):
        print(f"检测到原图，正在进行迭代生成: {base_image_path}")
        base64_img = encode_image(base_image_path)
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_img}"
            }
        })

    payload = {
        "model": "openai/gpt-5.4-image-2",
        "messages": [
            {
                "role": "user",
                "content": user_content if len(user_content) > 1 else prompt
            }
        ],
        "modalities": ["image", "text"]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            print(f"API 响应错误 ({response.status_code}): {response.text}")
        response.raise_for_status()
        result = response.json()

        if result.get("choices"):
            message = result["choices"][0]["message"]
            if message.get("images"):
                # 提取第一张生成的图片
                image_url = message["images"][0]["image_url"]["url"]
                save_base64_image(image_url, output_path)
            else:
                print("API 未返回图片数据。")
                if message.get("content"):
                    print(f"模型回复: {message['content']}")
        else:
            print(f"API 响应异常: {json.dumps(result, indent=2)}")

    except Exception as e:
        print(f"请求失败: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 图像生成与迭代工具")
    parser.add_argument("--prompt", required=True, help="生成指令")
    parser.add_argument("--output", required=True, help="输出图片路径")
    parser.add_argument("--base_image", help="原图路径（用于迭代修改）")
    
    args = parser.parse_args()
    
    generate_image(args.prompt, args.output, args.base_image)
