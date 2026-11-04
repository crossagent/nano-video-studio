import os

ps1_content = """# UTF-8 with BOM Script for Blender 4.2 Cleanup
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       Blender 4.2 残留清理与关联修复工具              " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. 杀死任何可能占用 4.2 文件的进程
Write-Host "`n[1/4] 检查并终止所有 Blender 进程..." -ForegroundColor Yellow
Get-Process -Name "blender*", "blender-launcher*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 500

# 2. 清理系统与用户的 4.2 注册表项
Write-Host "[2/4] 清理注册表中的 Blender 4.2 关联..." -ForegroundColor Yellow

try {
    Remove-ItemProperty -Path "HKLM:\\SOFTWARE\\Classes\\.blend\\OpenWithProgids" -Name "blender.4.2" -Force -ErrorAction SilentlyContinue
    Write-Host "  [+] 已从 HKLM OpenWithProgids 移除 blender.4.2" -ForegroundColor Green
} catch {}

if (Test-Path "HKLM:\\SOFTWARE\\Classes\\blender.4.2") {
    Remove-Item -Path "HKLM:\\SOFTWARE\\Classes\\blender.4.2" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [+] 已彻底删除 HKLM:\\SOFTWARE\\Classes\\blender.4.2" -ForegroundColor Green
}

try {
    Remove-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.blend\\OpenWithProgids" -Name "blender.4.2" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "HKCU:\\Software\\Classes\\blender.4.2" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [+] 已清理 HKCU 用户注册表残留" -ForegroundColor Green
} catch {}

# 3. 强化 5.2 默认关联
Write-Host "[3/4] 绑定 Blender 5.2 为唯一默认打开方式..." -ForegroundColor Yellow
try {
    Set-ItemProperty -Path "HKLM:\\SOFTWARE\\Classes\\.blend" -Name "(Default)" -Value "blender.5.2" -Force -ErrorAction SilentlyContinue
    New-ItemProperty -Path "HKLM:\\SOFTWARE\\Classes\\.blend\\OpenWithProgids" -Name "blender.5.2" -PropertyType None -Force -ErrorAction SilentlyContinue | Out-Null
    New-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.blend\\OpenWithProgids" -Name "blender.5.2" -PropertyType None -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Host "  [+] .blend 文件默认打开方式已锁定为 Blender 5.2" -ForegroundColor Green
} catch {}

# 4. 删除物理文件夹 C:\\Program Files\\Blender Foundation\\Blender 4.2
Write-Host "[4/4] 彻底删除 Program Files 目录残留..." -ForegroundColor Yellow
$dir = "C:\\Program Files\\Blender Foundation\\Blender 4.2"
if (Test-Path $dir) {
    # 夺权并赋予权限
    & takeown.exe /F "$dir" /R /D Y 2>$null | Out-Null
    & icacls.exe "$dir" /grant "administrators:F" /T /C /Q 2>$null | Out-Null
    
    # 删除文件夹
    cmd.exe /c "rmdir /s /q `"$dir`"" 2>$null | Out-Null
    
    if (-not (Test-Path $dir)) {
        Write-Host "  [+] 物理文件夹已成功彻底删除: $dir" -ForegroundColor Green
    } else {
        # 尝试二次删除
        Remove-Item -Path "$dir\*" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path "$dir" -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path $dir)) {
            Write-Host "  [+] 物理文件夹已成功彻底删除: $dir" -ForegroundColor Green
        } else {
            Write-Host "  [!] 仍有个别 DLL 文件被锁定，请重启电脑后再次运行本脚本即可彻底删除。" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  [+] 物理文件夹此前已不存在。" -ForegroundColor Green
}

# 刷新系统图标缓存
& ie4uinit.exe -show 2>$null | Out-Null

Write-Host "`n========================================================" -ForegroundColor Cyan
if (-not (Test-Path $dir)) {
    Write-Host "  [全部完成] Blender 4.2 残留已彻底清理干净！" -ForegroundColor Green
    Write-Host "  Windows '打开方式' 中只保留 Blender 5.2。" -ForegroundColor Green
} else {
    Write-Host "  [注册表与关联已清理完毕] 物理文件夹残留受系统占用锁定。" -ForegroundColor Yellow
    Write-Host "  重启后即可自动删除。" -ForegroundColor Yellow
}
Write-Host "========================================================" -ForegroundColor Cyan

Read-Host "`n请按回车键 (Enter) 退出窗口..."
"""

bat_content = '@echo off\r\npowershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process powershell.exe -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -File \"\"\"%~dp0clean_blender.ps1\"\"\"\' -Verb RunAs"\r\n'

desktop = os.path.expanduser('~/Desktop')

# Delete old bat / ps1 files from Desktop
for f in os.listdir(desktop):
    if 'blender4.2' in f.lower() or '清理blender' in f or f == 'clean_blender.ps1':
        try:
            os.remove(os.path.join(desktop, f))
            print('Cleaned from Desktop:', f)
        except Exception as e:
            print('Err cleaning:', e)

# Write to Desktop
ps1_path = os.path.join(desktop, 'clean_blender.ps1')
with open(ps1_path, 'wb') as f:
    f.write(b'\xef\xbb\xbf' + ps1_content.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))

bat_path = os.path.join(desktop, '一键清理Blender4.2.bat')
with open(bat_path, 'wb') as f:
    f.write(bat_content.encode('gbk'))

print('Successfully written to Desktop:')
print(' ', ps1_path)
print(' ', bat_path)

# Also write to platform/blender
pf_ps1 = r'd:\nano-video-studio\platform\blender\clean_blender.ps1'
pf_bat = r'd:\nano-video-studio\platform\blender\clean_blender_4.2.bat'
with open(pf_ps1, 'wb') as f:
    f.write(b'\xef\xbb\xbf' + ps1_content.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8'))
with open(pf_bat, 'wb') as f:
    f.write(bat_content.encode('gbk'))
print('Successfully written to platform/blender')
