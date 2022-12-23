#!/usr/bin/env python3
import base64
import json
import io
from PIL import Image
import urllib3
import boto3
import os
import concurrent.futures

INPUT_FOLDER = "test_images"
OUTPUT_FOLDER = "test_output"

cloudformation_client = boto3.client("cloudformation")


def get_lambda_url():
    response = cloudformation_client.describe_stacks(
        StackName="lambda-james-test-stack"
    )
    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        if output["OutputKey"] == "LambdaUrl":
            return output["OutputValue"]


def lambda_request(
    image_path, style_type, style_id, intrinsic_weight, extrinsic_weight
):
    if os.path.exists(
        os.path.join(
            OUTPUT_FOLDER, "style_output", style_type, str(style_id), image_path
        )
    ):
        print("skipping")
        return
    address = get_lambda_url()
    http = urllib3.PoolManager()
    if address is None:
        print("Could not get lambda url")
        exit(1)

    print(f"LambdaUrl -> {address}")

    img = Image.open(os.path.join(INPUT_FOLDER, image_path))
    img = img.convert("RGB")
    img.save(os.path.join(INPUT_FOLDER, image_path))

    with open(os.path.join(INPUT_FOLDER, image_path), "rb") as f:
        im_bytes = f.read()

    payload = json.dumps(
        {
            "inputImage": base64.encodebytes(im_bytes).decode("utf-8"),
            "intrinsicStyleWeight": intrinsic_weight,
            "extrinsicStyleWeight": extrinsic_weight,
            "style": style_type,
            "styleId": style_id,
        }
    ).encode("utf-8")

    response = http.request(
        "POST", address, headers={"Content-Type": "application/json"}, body=payload
    )

    response_payload = json.loads(response.data)

    im_b64 = response_payload["outputImage"]

    img_bytes = base64.b64decode(im_b64.encode("utf-8"))
    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))
    try:
        os.makedirs(
            os.path.join(OUTPUT_FOLDER, "style_output", style_type, str(style_id))
        )
    except Exception as e:
        pass
    img.save(
        os.path.join(
            OUTPUT_FOLDER, "style_output", style_type, str(style_id), image_path
        )
    )


def main():
    image_files = os.listdir(INPUT_FOLDER)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for image_path in image_files:
            futures.append(
                executor.submit(lambda_request, image_path, "none", 1, 0.0, 0.0)
            )
            for style_type in [
                "cartoon",
                "caricature",
                "anime",
                "arcane",
                "comic",
                "pixar",
                "slamdunk",
            ]:
                for style_id in [10, 20, 30, 40]:
                    futures.append(
                        executor.submit(
                            lambda_request, image_path, style_type, style_id, 0.6, 0.3
                        )
                    )


if __name__ == "__main__":
    main()
