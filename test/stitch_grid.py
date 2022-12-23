import os
import random
from PIL import Image, ImageOps
from PIL import ImageDraw, ImageFont


INPUT_FOLDER = "test_output/grid/caricature/id_30"
OUTPUT_PATH = "example_images/example_grid/stitched_grid.jpg"


def concat_images(image_paths, size, shape=None):
    # Open images and resize them
    width, height = size
    images = map(Image.open, image_paths)
    images = [ImageOps.fit(image, size, Image.ANTIALIAS) for image in images]

    # Create canvas for the final image with total size
    shape = shape if shape else (1, len(images))
    image_size = (width * shape[1], height * shape[0])
    image = Image.new("RGB", image_size)

    # Paste images into final image
    for row in range(shape[0]):
        for col in range(shape[1]):
            offset = width * col, height * row
            idx = row * shape[1] + col
            image.paste(images[idx], offset)

    return image


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


# Get list of image paths
folder = "images"
image_paths = [
    os.path.join(INPUT_FOLDER, f)
    for f in os.listdir(INPUT_FOLDER)
    if f.endswith(".jpg")
]

image_paths = sorted(image_paths)
# Create and save image grid
image = concat_images(image_paths, (200, 200), (5, 5))
# image = add_margin(image, 50, 50, 150, 250, "white")

# Add numbering
image.save(OUTPUT_PATH, "JPEG")
