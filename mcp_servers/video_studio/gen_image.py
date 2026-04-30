import requests
import json
import base64
import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_model_label(model_name):
    """提取模型简称用于文件名"""
    if not model_name: return "unknown"
    label = model_name.split("/")[-1]
    # 进一步简化常见模型名
    if "gpt-5.4" in label: return "gpt54"
    if "seedream" in label: return "seedream"
    return label.replace(".", "").replace("-", "")

def encode_image(image_path):
    """将本地图片转为 Base64 编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def save_image(url_or_base64, output_path):
    """保存图片（支持 URL 或 Base64）"""
    if url_or_base64.startswith("http"):
        try:
            response = requests.get(url_or_base64, stream=True, timeout=30)
            response.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"图片已保存至: {output_path} (来自 URL)")
        except Exception as e:
            print(f"下载图片失败: {str(e)}")
    else:
        data = url_or_base64
        if "," in data:
            data = data.split(",")[1]
        
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"图片已保存至: {output_path} (来自 Base64)")

def generate_via_openrouter(prompt, output_path, model, base_image_paths=None, size=None, aspect_ratio=None):
    """使用 OpenRouter API 生成图片"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("错误: 未找到 OPENROUTER_API_KEY")
        return

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/trae-ide",
        "X-Title": "Nano Video Studio",
    }

    # 构建多模态内容：交织模式 (Label + Image)
    user_content = []
    
    if ref_assets:
        for asset in ref_assets:
            path = asset.get('path')
            label = asset.get('label', os.path.basename(path) if path else "参考图")
            if path and os.path.exists(path):
                img_data = encode_image(path)
                # 插入文字描述标签
                user_content.append({"type": "text", "text": f"参考资产 ({label}):"})
                # 插入图片
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_data}"}
                })
    
    # 最后放入核心 Prompt
    user_content.append({"type": "text", "text": f"最终生图指令: {prompt}"})

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": user_content}],
        "modalities": ["image", "text"]
    }

    image_config = {}
    if size: image_config["image_size"] = size
    if aspect_ratio: image_config["aspect_ratio"] = aspect_ratio
    if image_config: payload["image_config"] = image_config

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        if result.get("choices"):
            message = result["choices"][0]["message"]
            if message.get("images"):
                img_data = message["images"][0]["image_url"]["url"]
                save_image(img_data, output_path)
            else:
                print(f"OpenRouter 未返回图片。完整响应: {json.dumps(result)}")
    except Exception as e:
        print(f"OpenRouter 请求失败: {str(e)}")

def generate_via_volcengine(prompt, output_path, model, base_image_paths=None, size=None):
    """使用火山引擎 (Volcengine Ark) Seedream 生成图片"""
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("错误: 未找到 ARK_API_KEY")
        return

    url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }

    v_size = size if size else "2k"
    if v_size == "1K": v_size = "2k" # Seedream 最小 2k

    payload = {
        "model": model,
        "prompt": prompt,
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": v_size,
        "stream": False,
        "watermark": True
    }

    if base_image_paths:
        if len(base_image_paths) == 1:
            img_path = base_image_paths[0]
            if os.path.exists(img_path):
                payload["image_url"] = f"data:image/png;base64,{encode_image(img_path)}"
        else:
            images = []
            for img_path in base_image_paths:
                if os.path.exists(img_path):
                    images.append(f"data:image/png;base64,{encode_image(img_path)}")
            payload["image"] = images

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code != 200:
            print(f"火山引擎请求失败 ({response.status_code}): {response.text}")
            return
        
        result = response.json()
        if "data" in result:
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                img_url = data[0].get("url")
                if img_url:
                    save_image(img_url, output_path)
                    return
        print(f"火山引擎未返回预期的图片格式: {json.dumps(result)}")
    except Exception as e:
        print(f"火山引擎请求异常: {str(e)}")

def generate_image(prompt, output_path, model=None, stage=None, base_image_paths=None, size=None, aspect_ratio=None, versioning=False):
    """统一生图入口"""
    # 确定模型
    if not model:
        if stage == "style":
            model = os.getenv("ART_STYLE_MODEL")
        elif stage == "character":
            model = os.getenv("CHARACTER_DESIGN_MODEL")
        elif stage == "scene":
            model = os.getenv("SCENE_DESIGN_MODEL")
        elif stage == "storyboard":
            model = os.getenv("STORYBOARD_MODEL")
        
        if not model:
            model = os.getenv("IMAGE_MODEL", "openai/gpt-5.4-image-2")
    
    # 版本化处理文件名
    if versioning:
        path = Path(output_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_label = get_model_label(model)
        new_filename = f"{path.stem}_{timestamp}_{model_label}{path.suffix}"
        output_path = str(path.parent / new_filename)

    print(f"正在使用模型 {model} 生成图片...")
    if versioning:
        print(f"启用版本化命名，实际输出路径: {output_path}")
    
    if "doubao-" in model:
        generate_via_volcengine(prompt, output_path, model, base_image_paths, size)
    else:
        generate_via_openrouter(prompt, output_path, model, base_image_paths, size, aspect_ratio)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI 图像生成工具 (支持多阶段模型配置)")
    parser.add_argument("--prompt", required=True, help="生成指令")
    parser.add_argument("--output", required=True, help="输出路径")
    parser.add_argument("--stage", choices=["style", "character", "scene", "storyboard"], help="任务阶段")
    parser.add_argument("--model", help="覆盖默认模型名称")
    parser.add_argument("--base_image", nargs='+', help="参考图路径")
    parser.add_argument("--size", help="图片尺寸")
    parser.add_argument("--aspect_ratio", help="比例")
    parser.add_argument("--versioning", action="store_true", help="启用版本化命名 (增加时间戳和模型标签)")
    
    args = parser.parse_args()
    
    generate_image(args.prompt, args.output, model=args.model, stage=args.stage, 
                   base_image_paths=args.base_image, size=args.size, 
                   aspect_ratio=args.aspect_ratio, versioning=args.versioning)
