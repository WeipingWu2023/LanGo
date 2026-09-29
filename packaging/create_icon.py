"""Draw the original detective-themed LanGo shortcut icon."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
image = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((24, 24, 1000, 1000), radius=225, fill='#102044')
draw.rounded_rectangle((57, 57, 967, 967), radius=195, outline='#4c79e3', width=20)
draw.ellipse((202, 165, 762, 725), fill='#f7fbff', outline='#f2b84b', width=66)
draw.ellipse((271, 234, 693, 656), fill='#f0c19a')
# Original detective avatar cues: swept hair, round glasses and red bow tie.
draw.polygon([(266, 365), (284, 225), (374, 126), (520, 108), (675, 196),
              (708, 362), (620, 293), (532, 245), (422, 276), (338, 364)], fill='#241f28')
draw.ellipse((330, 350, 460, 480), outline='#1a2235', width=18)
draw.ellipse((504, 350, 634, 480), outline='#1a2235', width=18)
draw.line((460, 412, 504, 412), fill='#1a2235', width=16)
draw.ellipse((386, 400, 420, 438), fill='#2457c6')
draw.ellipse((548, 400, 582, 438), fill='#2457c6')
draw.polygon([(480, 714), (390, 650), (302, 760), (408, 866), (480, 809),
              (552, 866), (658, 760), (570, 650)], fill='#cc3345')
draw.rounded_rectangle((661, 640, 835, 950), radius=68, fill='#f2b84b', outline='#ffffff', width=21)
image = image.resize((256, 256), Image.Resampling.LANCZOS)
(root / 'assets').mkdir(exist_ok=True)
image.save(root / 'assets' / 'lango.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
image.save(root / 'assets' / 'lango.png')
