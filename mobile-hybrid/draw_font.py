from PIL import Image, ImageDraw, ImageFont
font_path = "/Users/user/Documents/Astro-Nex-1.2.3/astronex/resources/Astro-Nex.ttf"
font = ImageFont.truetype(font_path, 40)
img = Image.new('RGB', (800, 200), color = (255, 255, 255))
d = ImageDraw.Draw(img)
d.text((10,10), "q w e r t y u i o p a s", font=font, fill=(0,0,0))
d.text((10,60), "Q W E R T Y U I O P A S", font=font, fill=(0,0,0))
d.text((10,110), "1 2 3 4 5 6 7 8 9 0", font=font, fill=(0,0,0))
img.save('/Users/user/Documents/Astro-Nex-1.2.3/mobile-hybrid/font_test.png')
