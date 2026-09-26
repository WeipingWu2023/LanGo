"""Draw Wordroom's simple book icon at Windows icon sizes."""
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent.parent
image = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((4, 4, 252, 252), radius=52, fill='#203d34')
draw.polygon([(45, 63), (112, 74), (128, 87), (144, 74), (211, 63), (211, 187), (145, 197), (128, 208), (111, 197), (45, 187)], fill='#f3f5f1')
draw.line([(128, 88), (128, 195)], fill='#23745d', width=6)
for y in (105, 132, 159):
    draw.line([(62, y), (108, y + 8)], fill='#8cb4a0', width=7)
    draw.line([(148, y + 8), (194, y)], fill='#8cb4a0', width=7)
(root / 'assets').mkdir(exist_ok=True)
image.save(root / 'assets' / 'wordroom.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
image.save(root / 'assets' / 'wordroom.png')
