import os
import numpy as np
import torch
from argparse import Namespace
from torchvision import transforms
from torch.nn import functional as F
from model.dualstylegan import DualStyleGAN
from datetime import datetime
import base64
from PIL import Image
import io
import json
from random import randint
from multiprocessing import Pipe, Process
from validation import validate_user_payload, UserPayloadException
import onnxruntime
import multiprocessing as mp

mp.set_start_method("fork")

os.environ["CUDA_VISIBLE_DEVICES"] = ""
CODE_DIR = "DualStyleGAN"
device = "cpu"

MODEL_DIR = os.path.join(os.getcwd(), CODE_DIR, "checkpoint")
DATA_DIR = os.path.join(os.getcwd(), CODE_DIR, "data")

RESPONSE_HEADERS = {
    "Access-Control-Allow-Headers": "Content-Type,access-control-allow-origin,content-type",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}

MODEL_PATHS = {
    "encoder": {"id": "1NgI4mPkboYvYw3MWcdUaQhkr0OWgs9ej", "name": "encoder.pt"},
    "cartoon-G": {"id": "1exS9cSFkg8J4keKPmq2zYQYfJYC5FkwL", "name": "generator.pt"},
    "cartoon-N": {"id": "1JSCdO0hx8Z5mi5Q5hI9HMFhLQKykFX5N", "name": "sampler.pt"},
    "cartoon-S": {
        "id": "1ce9v69JyW_Dtf7NhbOkfpH77bS_RK0vB",
        "name": "refined_exstyle_code.npy",
    },
    "caricature-G": {"id": "1BXfTiMlvow7LR7w8w0cNfqIl-q2z0Hgc", "name": "generator.pt"},
    "caricature-N": {"id": "1eJSoaGD7X0VbHS47YLehZayhWDSZ4L2Q", "name": "sampler.pt"},
    "caricature-S": {
        "id": "1-p1FMRzP_msqkjndRK_0JasTdwQKDsov",
        "name": "refined_exstyle_code.npy",
    },
    "anime-G": {"id": "1BToWH-9kEZIx2r5yFkbjoMw0642usI6y", "name": "generator.pt"},
    "anime-N": {"id": "19rLqx_s_SUdiROGnF_C6_uOiINiNZ7g2", "name": "sampler.pt"},
    "anime-S": {
        "id": "17-f7KtrgaQcnZysAftPogeBwz5nOWYuM",
        "name": "refined_exstyle_code.npy",
    },
    "arcane-G": {"id": "15l2O7NOUAKXikZ96XpD-4khtbRtEAg-Q", "name": "generator.pt"},
    "arcane-N": {"id": "1fa7p9ZtzV8wcasPqCYWMVFpb4BatwQHg", "name": "sampler.pt"},
    "arcane-S": {"id": "1z3Nfbir5rN4CrzatfcgQ8u-x4V44QCn1", "name": "exstyle_code.npy"},
    "comic-G": {"id": "1_t8lf9lTJLnLXrzhm7kPTSuNDdiZnyqE", "name": "generator.pt"},
    "comic-N": {"id": "1RXrJPodIn7lCzdb5BFc03kKqHEazaJ-S", "name": "sampler.pt"},
    "comic-S": {"id": "1ZfQ5quFqijvK3hO6f-YDYJMqd-UuQtU-", "name": "exstyle_code.npy"},
    "pixar-G": {"id": "1TgH7WojxiJXQfnCroSRYc7BgxvYH9i81", "name": "generator.pt"},
    "pixar-N": {"id": "18e5AoQ8js4iuck7VgI3hM_caCX5lXlH_", "name": "sampler.pt"},
    "pixar-S": {"id": "1I9mRTX2QnadSDDJIYM_ntyLrXjZoN7L-", "name": "exstyle_code.npy"},
    "slamdunk-G": {"id": "1MGGxSCtyf9399squ3l8bl0hXkf5YWYNz", "name": "generator.pt"},
    "slamdunk-N": {"id": "1-_L7YVb48sLr_kPpOcn4dUq7Cv08WQuG", "name": "sampler.pt"},
    "slamdunk-S": {
        "id": "1Dgh11ZeXS2XIV2eJZAExWMjogxi_m_C8",
        "name": "exstyle_code.npy",
    },
}


def run_alignment(filepath):
    import dlib
    from model.encoder.align_all_parallel import align_face

    modelname = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")
    predictor = dlib.shape_predictor(modelname)
    aligned_image = align_face(filepath=filepath, predictor=predictor)
    del predictor
    return aligned_image


def serialize_image(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    im_bytes = img_byte_arr.getvalue()
    im_b64 = base64.b64encode(im_bytes).decode("utf8")
    return im_b64


def deserialize_image(im_b64):
    im_bytes = base64.b64decode(im_b64.encode("utf8"))
    return Image.open(io.BytesIO(im_bytes))


def face_alignment(image_path, conn):

    I = run_alignment(image_path)

    conn.send([I])
    conn.close()


def to_numpy(tensor):
    return (
        tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
    )


def encode(ort_encoder, I):

    # compute ONNX Runtime output prediction
    start_onnx_runtime = datetime.now()

    ort_inputs = {ort_encoder.get_inputs()[0].name: I}

    np.save("/tmp/encoder_out.npy", ort_encoder.run(None, ort_inputs)[0])

    print(f"The inference time is {datetime.now() - start_onnx_runtime}")


def decode(
    generator,
    instyle,
    exstyles,
    stylename,
    intrinsic_style_weight,
    extrinsic_style_weight,
):
    with torch.no_grad():
        latent = torch.tensor(exstyles[stylename]).repeat(2, 1, 1).to(device)
        latent[1, 7:18] = instyle[0, 7:18]

        print("Generating image")

        image_generation_time = datetime.now()

        exstyle = generator.generator.style(
            latent.reshape(latent.shape[0] * latent.shape[1], latent.shape[2])
        ).reshape(latent.shape)

        img_gen, _ = generator(
            [instyle.repeat(2, 1, 1)],
            exstyle,
            z_plus_latent=True,
            truncation=0.7,
            truncation_latent=0,
            use_res=True,
            interp_weights=[intrinsic_style_weight] * 7 + [extrinsic_style_weight] * 11,
        )
        img_gen = torch.clamp(img_gen.detach(), -1, 1)
        print(
            f"Finished generating first image: {datetime.now() - image_generation_time}"
        )
    return img_gen


def load_encoder(enc_model_path):
    # Encoder
    start_onnx_load = datetime.now()
    ort_encoder = onnxruntime.InferenceSession(enc_model_path)
    print(f"Loading onnx model took {datetime.now() - start_onnx_load}")

    return ort_encoder


def load_decoder(gen_model_path):
    gen_loading_time = datetime.now()
    ckpt = torch.load(gen_model_path, map_location="cpu")
    generator = DualStyleGAN(1024, 512, 8, 2, res_index=6)
    generator.eval()
    generator.load_state_dict(ckpt["g_ema"])
    generator = generator.to(device)
    print(f"Loading generator ckpt finished {datetime.now() - gen_loading_time}")
    return generator


def encode_parallel(parent_conn, enc_model_path):
    enc = load_encoder(enc_model_path)
    result = parent_conn.recv()
    encode(enc, result[0])
    parent_conn.close()


def lambda_handler(event, context):
    http_method = event.get("requestContext", {}).get("httpMethod", "Unknown HTTP method")
    source_ip = event.get("requestContext", {}).get("identity", {}).get("sourceIp", "Unknown Ip")
    print(f"{source_ip}->{http_method}")

    if http_method == "OPTIONS":
        return {"statusCode": 200, "headers": RESPONSE_HEADERS}

    if "body" not in event:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"error": "No request body passed, serialized image required"}
            ),
            "headers": RESPONSE_HEADERS,
        }
    try:
        raw_payload = json.loads(event.get("body", {}))
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Request body must be valid JSON: {e}"}),
            "headers": RESPONSE_HEADERS,
        }

    try:
        payload = validate_user_payload(raw_payload)
    except UserPayloadException as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
            "headers": RESPONSE_HEADERS,
        }

    print("Loading styles")
    style_loading_time = datetime.now()
    # load extrinsic style code
    exstyles = np.load(
        os.path.join(
            MODEL_DIR, payload.style, MODEL_PATHS[payload.style + "-S"]["name"]
        ),
        allow_pickle="TRUE",
    ).item()
    print(f"Loading styles finished {datetime.now() - style_loading_time}")

    # Try to load the style image
    try:
        stylename = list(exstyles.keys())[payload.style_variant]
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "error": f"Style variant not valid for this style. Please select between 0 and {len(list(exstyles.keys())) - 1}"
                }
            ),
            "headers": RESPONSE_HEADERS,
        }

    print("Deserializing image")
    time = datetime.now()
    img = deserialize_image(payload.input_image)
    img = img.convert("RGB")
    img.save("/tmp/image.jpg")
    print(f"Finished de-serializing the image: {datetime.now() - time}")

    image_path = "/tmp/image.jpg"
    gen_model_path = os.path.join(MODEL_DIR, payload.style, "generator.pt")
    enc_model_path = os.path.join(MODEL_DIR, "encoder.onnx")
    # Create a pipe for sending the image to the encoder process ready for after it has finished loading in
    print("Creating Pipes")
    child_conn, parent_conn = Pipe()

    # Run the encoder in a seperate process with no torch dependency
    print("Creating process")
    enc_process = Process(target=encode_parallel, args=(parent_conn, enc_model_path))
    print("Starting encoder process")
    enc_process.start()

    # Align and transform the input image
    I = run_alignment(image_path)

    transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(256),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ]
    )
    # Pull the aligned face and convert to a numpy array
    I = transform(I).unsqueeze(dim=0).detach().numpy()

    # Load the generator
    generator = load_decoder(gen_model_path)

    # Send the image to the encoder for encoding
    child_conn.send([I])

    # Wait for the encoder to finish encoding and saving the result
    enc_process.join()

    # Load in the encoded image
    instyle = torch.from_numpy(np.load("/tmp/encoder_out.npy"))

    # Decode the image
    img_gen = decode(
        generator,
        instyle,
        exstyles,
        stylename,
        payload.intrinsic_style_weight,
        payload.extrinsic_style_weight,
    )

    # Post process the image
    print("Serializing image")
    serialized_image_time = datetime.now()
    serialized_image = serialize_image(
        Image.fromarray(
            (
                (
                    img_gen[0, :, :, :].detach().numpy().squeeze().transpose(1, 2, 0)
                    + 1.0
                )
                * 127.5
            ).astype(np.uint8),
            "RGB",
        )
    )
    print(f"Finished Serializing Image : {datetime.now() - serialized_image_time}")

    return {
        "statusCode": 200,
        "body": json.dumps({"outputImage": serialized_image}),
        "headers": RESPONSE_HEADERS,
    }
