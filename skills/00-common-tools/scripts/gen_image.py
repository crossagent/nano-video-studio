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

def generate_image(prompt, output_path, base_image_paths=None, api_key=None, size=None, aspect_ratio=None):
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
    
    if base_image_paths:
        if isinstance(base_image_paths, str):
            base_image_paths = [base_image_paths]
            
        for img_path in base_image_paths:
            if os.path.exists(img_path):
                print(f"检测到参考图，正在加入 Prompt: {img_path}")
                base64_img = encode_image(img_path)
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_img}"
                    }
                })
            else:
                print(f"警告: 参考图路径不存在: {img_path}")

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

    # 添加图像配置
    image_config = {}
    if size:
        image_config["image_size"] = size
    if aspect_ratio:
        image_config["aspect_ratio"] = aspect_ratio
    
    if image_config:
        payload["image_config"] = image_config

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
    parser.add_argument("--base_image", nargs='+', help="参考图路径，支持多个（用于角色一致性、场景参考等）")
    parser.add_argument("--size", help="图片尺寸 (如: 0.5K, 1K, 2K, 4K)")
    parser.add_argument("--aspect_ratio", help="图片比例 (如: 1:1, 16:9, 9:16)")
    
    args = parser.parse_args()
    
    generate_image(args.prompt, args.output, args.base_image, size=args.size, aspect_ratio=args.aspect_ratio)
