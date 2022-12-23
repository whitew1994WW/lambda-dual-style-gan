import os
import random
import shutil
from PIL import Image, ImageOps
from PIL import ImageDraw, ImageFont


INPUT_FOLDER = "test_images/"


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


def add_id_annotation(image):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("Aaargh.ttf", 26)
    # THe dictionary iterated below is for the alignment of text to the centre
    for i, style_item in enumerate(
        {
            "Source Image": 10,
            "Variant 10": 35,
            "Variant 20": 35,
            "Variant 30": 35,
            "Variant 40": 35,
        }.items()
    ):
        draw.text(
            (style_item[1] + i * 200, 10), style_item[0], (0, 100, 255), font=font
        )
    return image


# Get list of image paths


source_image_names = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".jpg")]

# Generate an example style image for each source image and style_id so we have a selection to choose from
for image_filename in source_image_names:
    source_image_path = os.path.join(INPUT_FOLDER, image_filename)
    for style in [
        "cartoon",
        "caricature",
        "anime",
        "arcane",
        "comic",
        "pixar",
        "slamdunk",
    ]:
        style_paths = [source_image_path]
        for style_id in [10, 20, 30, 40]:
            style_paths.append(
                os.path.join(
                    "test_output", "style_output", style, str(style_id), image_filename
                )
            )
        output_folder = os.path.join(
            "test_output", "id_grid", style, image_filename[:-4]
        )

        # Make the new directory
        try:
            os.makedirs(output_folder)
        except Exception as e:
            pass

        # Move each image into the new folder
        for i, path in enumerate(style_paths):
            shutil.copyfile(path, os.path.join(output_folder, str(i) + ".jpg"))
