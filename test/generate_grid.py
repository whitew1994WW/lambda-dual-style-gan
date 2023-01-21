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
TEST_IMAGE = "pexels-karolina-grabowska-7603002.jpg"
STYLE_TYPE = "caricature"
STYLE_ID = 30

cloudformation_client = boto3.client("cloudformation")


def get_lambda_url():
    response = cloudformation_client.describe_stacks(
        StackName="lambda-james-test-stack"
    )
    outputs = response["Stacks"][0]["Outputs"]
    for output in outputs:
        if output["OutputKey"] == "LambdaUrl":
            return output["OutputValue"]


def lambda_request(image_path, style_type, style_id, int_weight, ext_weight):
    address = get_lambda_url()
    http = urllib3.PoolManager()
    if address is None:
        print("Could not get lambda url")
        exit(1)

    print(f"LambdaUrl -> {address}")

    with open(os.path.join(INPUT_FOLDER, image_path), "rb") as f:
        im_bytes = f.read()

    payload = json.dumps(
        {
            "inputImage": base64.encodebytes(im_bytes).decode("utf-8"),
            "intrinsicStyleWeight": int_weight,
            "extrinsicStyleWeight": ext_weight,
            "style": STYLE_TYPE,
            "styleId": style_id,
        }
    ).encode("utf-8")

    response = http.request(
        "POST", address, headers={"Content-Type": "application/json"}, body=payload
    )

    print(f"=> {response.data}")

    response_payload = json.loads(response.data)

    im_b64 = response_payload["outputImage"]

    img_bytes = base64.b64decode(im_b64.encode("utf-8"))
    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))
    img.save(
        os.path.join(
            OUTPUT_FOLDER,
            "grid",
            style_type,
            "id_" + str(style_id),
            str(ext_weight) + "_" + str(int_weight) + "_" + image_path,
        )
    )


def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            os.makedirs(
                os.path.join(OUTPUT_FOLDER, "grid", STYLE_TYPE, "id_" + str(STYLE_ID))
            )
        except Exception as e:
            pass
        futures = []
        for int_weight in [0.0, 0.2, 0.4, 0.6, 0.8]:
            for ext_weight in [0.0, 0.2, 0.4, 0.6, 0.8]:
                futures.append(
                    executor.submit(
                        lambda_request,
                        TEST_IMAGE,
                        STYLE_TYPE,
                        STYLE_ID,
                        int_weight,
                        ext_weight,
                    )
                )


if __name__ == "__main__":
    main()
