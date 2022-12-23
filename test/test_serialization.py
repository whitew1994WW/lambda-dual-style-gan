#!/usr/bin/env python3
import base64
import json
import io
from PIL import Image
import requests

def main():
    image_file = "test_images/pexels-cottonbro-10319506.jpg"
    output_file = "test_output.jpg"
    address = "https://style-transfer.plutotech.xyz"

    if address is None:
        print("Could not get lambda url")
        exit(1)

    print(f"LambdaUrl -> {address}")

    with open(image_file, "rb") as f:
        im_bytes = f.read()

    payload = {
        "inputImage": base64.encodebytes(im_bytes).decode("utf-8"),
        "intrinsicStyleWeight": 0.5,
        "extrinsicStyleWeight": 0.6,
        "style": "anime",
    }

    response = requests.post(
        address, headers={"Content-Type": "application/json"}, json=payload
    )

    if not response.ok:
        print(f"Failed to make request: {response.text}")
        exit(1)

    response_payload = response.json()

    im_b64 = response_payload["outputImage"]

    img_bytes = base64.b64decode(im_b64.encode("utf-8"))
    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))

    img.save(output_file)


if __name__ == "__main__":
    main()
