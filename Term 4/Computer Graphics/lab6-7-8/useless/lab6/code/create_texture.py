from PIL import Image

def create_checkerboard(width=256, height=256, tile_size=32):
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            if (x // tile_size) % 2 == (y // tile_size) % 2:
                pixels[x, y] = (255, 255, 255)
            else:
                pixels[x, y] = (0, 0, 0)
    img.save("texture.bmp")

create_checkerboard()