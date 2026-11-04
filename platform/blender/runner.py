"""
platform/blender/runner.py
Blender 5.x 平台统一执行器 (Platform Blender Python Runner)
通过 Python 调用，免受 Windows PowerShell ExecutionPolicy 策略限制。
"""

import sys
import os
import subprocess
import shutil

def find_blender():
    # 1. 检查环境变量
    env_path = os.environ.get("BLENDER_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    # 2. 检查常见安装路径
    candidates = [
        r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
    ]
    for cand in candidates:
        if os.path.exists(cand):
            return cand
            
    # 3. 检查系统 PATH
    path_bin = shutil.which("blender") or shutil.which("blender.exe")
    if path_bin and os.path.exists(path_bin):
        return path_bin
        
    return None

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Blender 平台统一执行工具")
    parser.add_argument("--script", "-s", type=str, help="需要执行的 Python 脚本路径")
    parser.add_argument("--blend", "-b_file", type=str, help="预加载的 .blend 工程文件")
    parser.add_argument("--gui", action="store_true", help="是否开启 GUI 窗口（默认无头后台运行）")
    
    # 截取传给脚本的剩余参数（-- 之后的参数）
    raw_args = sys.argv[1:]
    script_extra_args = []
    if "--" in raw_args:
        idx = raw_args.index("--")
        blender_runner_args = raw_args[:idx]
        script_extra_args = raw_args[idx + 1:]
    else:
        blender_runner_args = raw_args
        
    args, unknown = parser.parse_known_args(blender_runner_args)
    
    blender_exe = find_blender()
    if not blender_exe:
        print("[Platform/Blender ERROR] 未找到 Blender 可执行程序，请检查安装路径。", file=sys.stderr)
        sys.exit(1)
        
    cmd = [blender_exe]
    if not args.gui:
        cmd.append("-b")
        
    if args.blend:
        cmd.append(os.path.abspath(args.blend))
        
    if args.script:
        cmd.extend(["--python", os.path.abspath(args.script)])
        
    if script_extra_args:
        cmd.append("--")
        cmd.extend(script_extra_args)
        
    print(f"[Platform/Blender] 执行程序: {blender_exe}")
    print(f"[Platform/Blender] 执行命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
