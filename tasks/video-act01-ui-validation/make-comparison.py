from pathlib import Path
from PIL import Image, ImageDraw
import subprocess,sys
id=sys.argv[1]; p=Path('tasks/video-act01-ui-validation/work');p.mkdir(exist_ok=True); ff=next(Path('tasks/blender/act01-shared-world/work/deps/imageio_ffmpeg/binaries').glob('ffmpeg*.exe')); dur=4 if id=='09' else 5 if id=='10' else 3
videos=[Path(f'tasks/act01-visual-storyboards/output/shots/shot_{id}/whitebox.mp4'),Path(f'tasks/act01-visual-storyboards/output/final-shots/shot_{id}.mp4')]; canvas=Image.new('RGB',(960,400),'white');draw=ImageDraw.Draw(canvas)
for row,video in enumerate(videos):
 for col,t in enumerate([0,dur/2,dur-.1]):
  pth=p/f'shot{id}_{row}_{col}.png';subprocess.run([str(ff),'-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-y',str(pth)],check=True);im=Image.open(pth);im.thumbnail((316,165));canvas.paste(im,(320*col,200*row+25));draw.text((320*col,200*row+5),f'{["whitebox","generated"][row]} {t:.1f}s',fill='black')
canvas.save(p/f'shot{id}_comparison.jpg')
