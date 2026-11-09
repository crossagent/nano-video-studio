from pathlib import Path
import subprocess
ff=next(Path('tasks/blender/act01-shared-world/work/deps/imageio_ffmpeg/binaries').glob('ffmpeg*.exe'))
cmd=[str(ff),'-hide_banner','-loglevel','error','-y']; filters=[]; pairs=[]
for i in range(1,11):
 cmd += ['-i',f'tasks/act01-visual-storyboards/output/final-shots/shot_{i:02}.mp4']
 duration=4 if i==9 else 3
 filters += [f'[{i-1}:v]trim=duration={duration},setpts=PTS-STARTPTS[v{i}]',f'[{i-1}:a]atrim=duration={duration},asetpts=PTS-STARTPTS,aresample=48000[a{i}]']
 pairs.append(f'[v{i}][a{i}]')
filters.append(''.join(pairs)+'concat=n=10:v=1:a=1[v][a]')
cmd += ['-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','192k','-movflags','+faststart','tasks/act01-capcut-edit/output/act01_assembly_preview.mp4']
subprocess.run(cmd,check=True)
