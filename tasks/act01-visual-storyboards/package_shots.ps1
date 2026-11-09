$ErrorActionPreference = 'Stop'
$root = 'D:/nano-video-studio/tasks/act01-visual-storyboards'
$ffmpeg = (Get-ChildItem 'D:/nano-video-studio/tasks/blender/act01-shared-world/work/deps' -Recurse -Filter '*ffmpeg*.exe' | Select-Object -First 1).FullName
$video = 'D:/nano-video-studio/tasks/blender/act01-shared-world/output/act01_shared_world_camera_fix.mp4'
$frames = 'D:/nano-video-studio/tasks/blender/act01-shared-world/work/frames_camera_fix'
$sheets = @("$root/work/sheet_01-05_no_labels.png", "$root/work/sheet_06-10_no_labels.png")
$starts = @(1,73,145,217,289,361,433,505,577,673)
$ends = @(72,144,216,288,360,432,504,576,672,792)
$names = @('麦原风暴','收割机跟拍','驾驶舱','避难所防御塔','板房人物','地震仪','板房地震','刀锋女王','神庙裂谷','神庙大门')
$ys = @(3,310,617,925,1232)
for ($i = 0; $i -lt 10; $i++) {
    $id = '{0:D2}' -f ($i+1)
    $dir = "$root/output/shots/shot_$id"
    New-Item -ItemType Directory -Force $dir | Out-Null
    $start = $starts[$i]; $end = $ends[$i]; $count = $end - $start + 1
    $filter = "trim=start_frame=$($start-1):end_frame=$end,setpts=PTS-STARTPTS"
    & $ffmpeg -hide_banner -loglevel error -y -i $video -vf $filter -an -c:v libx264 -crf 18 -pix_fmt yuv420p "$dir/whitebox.mp4"
    if ($LASTEXITCODE -ne 0) { throw "Video extraction failed for $id" }
    $sheet = $sheets[[int][math]::Floor($i/5)]
    $y = $ys[$i%5]
    & $ffmpeg -hide_banner -loglevel error -y -i $sheet -vf "crop=1020:300:2:$y" -frames:v 1 -update 1 "$dir/first_frame_candidate.png"
    if ($LASTEXITCODE -ne 0) { throw "Image extraction failed for $id" }
    Copy-Item (Join-Path $frames ('frame_{0:D4}.png' -f $start)) "$dir/whitebox_first_frame.png"
    $seconds = $count / 24
    $note = if ($i -eq 7) { '该画面参考第 545 帧（镜头中段），不是第 505 帧；与白模首帧不严格匹配，建议针对第 505 帧重新制作首帧。' } else { '该画面由分镜图裁出，参考同镜头白模及剧本设计，构图和主体比例仅近似；尚未验证与白模首帧精确对齐。' }
    $info = @"
# Shot $id — $($names[$i])

- 白模：whitebox.mp4，原时间轴 $start–$end 帧，$count 帧 / 24 fps，$seconds 秒。
- 白模真实首帧：whitebox_first_frame.png（原第 $start 帧）。
- 视觉首帧候选：first_frame_candidate.png，来自角色修订版分镜表的对应画格，经去编号后裁出，并非从生成视频导出。
- 对齐情况：$note
- 画幅：白模为 1920×804（约 2.39:1），候选图为 1020×300（约 3.4:1）；接入模型前需要重新构图或适配画幅。
- 这些文件是配对素材，尚未实际通过模型验证首帧与运动白模同时生效。
"@
    Set-Content -Encoding utf8 "$dir/README.md" $info
    Write-Output "PACKAGED $id $start-$end $count"
}
