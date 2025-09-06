from PIL import Image, ImageDraw

# Create blank image (example size, change as needed)
width, height = 2331, 1025
image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
draw = ImageDraw.Draw(image)

# Tile size
tile_width = 129
tile_height = 129

# Draw vertical lines
for x in range(0, width, tile_width):
    draw.line([(x, 0), (x, height)], fill="red", width=1)

# Draw horizontal lines
for y in range(0, height, tile_height):
    draw.line([(0, y), (width, y)], fill="red", width=1)

# Save to file
image.save("output/filename.png")

