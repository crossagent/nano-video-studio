<#
.SYNOPSIS
    Blender 平台统一执行工具 (Platform Blender Runner)
.DESCRIPTION
    负责自动定位 Blender 5.x 运行程序，统一管理无头执行（Headless）、Python 脚本注入与参数传递。
.PARAMETER Script
    需要由 Blender 内部 Python 引擎执行的脚本路径。
.PARAMETER BlendFile
    可选，需要预先加载的 .blend 工程文件路径。
.PARAMETER Headless
    是否以静默无头（-b）模式运行，默认为 $true。
.PARAMETER ScriptArgs
    传递给 Python 脚本的自定义参数列表（通过 -- 传递）。
#>
param (
    [Parameter(Mandatory=$false)]
    [string]$Script,

    [Parameter(Mandatory=$false)]
    [string]$BlendFile,

    [Parameter(Mandatory=$false)]
    [bool]$Headless = $true,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ScriptArgs
)

# 1. 自动定位 Blender 可执行文件
$blenderPath = $env:BLENDER_PATH

if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
    $candidatePaths = @(
        "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
        "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
    )
    foreach ($cand in $candidatePaths) {
        if (Test-Path $cand) {
            $blenderPath = $cand
            break
        }
    }
}

if (-not $blenderPath) {
    $cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        $blenderPath = $cmd.Source
    }
}

if (-not $blenderPath -or -not (Test-Path $blenderPath)) {
    Write-Error "[Platform/Blender] 未找到 Blender 可执行程序，请检查安装或设置环境变量 BLENDER_PATH。"
    exit 1
}

Write-Host "[Platform/Blender] 使用程序: $blenderPath"

# 2. 构造启动参数
$arguments = @()

if ($Headless) {
    $arguments += "-b"
}

if ($BlendFile) {
    $arguments += "`"$BlendFile`""
}

if ($Script) {
    $resolvedScript = Resolve-Path $Script -ErrorAction SilentlyContinue
    if (-not $resolvedScript) {
        $resolvedScript = $Script
    }
    $arguments += "--python"
    $arguments += "`"$resolvedScript`""
}

if ($ScriptArgs -and $ScriptArgs.Count -gt 0) {
    $arguments += "--"
    foreach ($arg in $ScriptArgs) {
        $arguments += "`"$arg`""
    }
}

# 3. 执行 Blender 命令
$argString = $arguments -join " "
Write-Host "[Platform/Blender] 正在执行: & `"$blenderPath`" $argString"

$proc = Start-Process -FilePath $blenderPath -ArgumentList $arguments -NoNewWindow -Wait -PassThru
exit $proc.ExitCode
