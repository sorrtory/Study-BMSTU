from PIL import Image

img = Image.open("second.tif")  # or .jpg
img.convert("RGB").save("texture2.bmp")  # save as 24-bit BMP
