"""Draw the original detective-themed Wordroom shortcut icon."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
image = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((24, 24, 1000, 1000), radius=225, fill='#102044')
draw.rounded_rectangle((57, 57, 967, 967), radius=195, outline='#4c79e3', width=20)
draw.ellipse((202, 165, 762, 725), fill='#f7fbff', outline='#f2b84b', width=66)
draw.ellipse((271, 234, 693, 656), fill='#d9e7ff')
draw.rounded_rectangle((661, 640, 835, 950), radius=68, fill='#f2b84b', outline='#ffffff', width=21)
draw.polygon([(480, 300), (516, 397), (620, 398), (539, 462), (569, 565),
              (480, 508), (391, 565), (421, 462), (340, 398), (444, 397)], fill='#2457c6')
image = image.resize((256, 256), Image.Resampling.LANCZOS)
(root / 'assets').mkdir(exist_ok=True)
image.save(root / 'assets' / 'wordroom.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
image.save(root / 'assets' / 'wordroom.png')
