import io
from tracemalloc import start
import numpy as np

from torch import nn
import torch.utils.model_zoo as model_zoo
import torch.onnx
import torch
from torch.nn import functional as F
import os
from model.dualstylegan import DualStyleGAN
from datetime import datetime
from PIL import Image
from torchvision import transforms
import onnx
import onnxruntime
import cv2

os.environ["CUDA_VISIBLE_DEVICES"] = ""
CODE_DIR = "DualStyleGAN"
device = "cpu"

MODEL_DIR = os.path.join(os.getcwd(), CODE_DIR, "checkpoint")
DATA_DIR = os.path.join(os.getcwd(), CODE_DIR, "data")

SAVE_ENCODER = False

STYLE_VARIANT = 10
STYLE = "caricature"
INTRINSIC_STYLE_WEIGHT = 0.6
EXTRINSIC_STYLE_WEIGHT = 0.2

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


def load_encoder():
    print(f"Encoder procID: {os.getpid()}")
    from model.encoder.psp import pSp
    import torch
    from argparse import Namespace
    from torch.nn import functional as F

    enc_model_path = os.path.join(MODEL_DIR, "encoder.pt")
    enc_opts_path = os.path.join(CODE_DIR, "encoder_opts.pt")
    enc_loading_time = datetime.now()
    opts = torch.load(enc_opts_path, map_location="cpu")
    opts["checkpoint_path"] = enc_model_path
    print(f"Time after just loading file is {datetime.now() - enc_loading_time}")
    opts = Namespace(**opts)
    opts.device = device
    encoder = pSp(opts)
    encoder.eval()
    encoder = encoder.to(device)
    print(f"Loading encoder ckpt finished {datetime.now() - enc_loading_time}")
    return encoder


def load_image(img):
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ]
    )
    img = transform(img)
    return img.unsqueeze(dim=0)


def load_decoder():
    gen_model_path = os.path.join(MODEL_DIR, "caricature", "generator.pt")
    gen_loading_time = datetime.now()
    ckpt = torch.load(gen_model_path, map_location="cpu")
    generator = DualStyleGAN(1024, 512, 8, 2, res_index=6)
    generator.eval()
    generator.load_state_dict(ckpt["g_ema"])
    generator = generator.to(device)
    print(f"Loading generator ckpt finished {datetime.now() - gen_loading_time}")
    return generator


def run_alignment(filepath):
    import dlib
    from model.encoder.align_all_parallel import align_face

    modelname = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")
    predictor = dlib.shape_predictor(modelname)
    aligned_image = align_face(filepath=filepath, predictor=predictor)
    return aligned_image


def save_image(img, filename):
    tmp = ((img.numpy().squeeze().transpose(1, 2, 0) + 1.0) * 127.5).astype(np.uint8)
    cv2.imwrite(filename, cv2.cvtColor(tmp, cv2.COLOR_RGB2BGR))


# print(torch.load('DualStyleGAN/encoder_opts.pt'))

exstyles = np.load(
    os.path.join(MODEL_DIR, STYLE, MODEL_PATHS[STYLE + "-S"]["name"]),
    allow_pickle="TRUE",
).item()
stylename = list(exstyles.keys())[STYLE_VARIANT]

I = run_alignment("DualStyleGAN/test_image.jpg")
transform = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(256),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ]
)


# Pull the aligned face
I = transform(I).unsqueeze(dim=0).to(device)
save_image(I, "aligned_face.jpg")
encoder = load_encoder()
torch_out = encoder(
    I,
    randomize_noise=False,
    return_latents=True,
    z_plus_latent=True,
    resize=False,
)

if SAVE_ENCODER:
    # Export the model
    torch.onnx.export(
        encoder,  # model being run
        I,  # model input (or a tuple for multiple inputs)
        "DualStyleGAN/checkpoint/encoder.onnx",  # where to save the model (can be a file or file-like object)
        export_params=True,  # store the trained parameter weights inside the model file
        opset_version=11,  # the ONNX version to export the model to
        do_constant_folding=True,  # whether to execute constant folding for optimization
        input_names=["input"],  # the model's input names
        output_names=["output"],  # the model's output names
        dynamic_axes={
            "input": {0: "batch_size"},  # variable length axes
            "output": {0: "batch_size"},
        },
    )

# # Load decoder
generator = load_decoder()


# Encoder
start_onnx_load = datetime.now()
ort_session = onnxruntime.InferenceSession("encoder.onnx")
print(f"Loading onnx model took {datetime.now() - start_onnx_load}")


def to_numpy(tensor):
    return (
        tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()
    )


# compute ONNX Runtime output prediction
start_onnx_runtime = datetime.now()

ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(I)}

ort_outs = torch.from_numpy(ort_session.run(None, ort_inputs)[0])


print(f"The inference time is {datetime.now() - start_onnx_runtime}")

# compare ONNX Runtime and PyTorch results
np.testing.assert_allclose(
    to_numpy(torch_out.squeeze()), ort_outs[0], rtol=1e-03, atol=1e-05
)

onnx_instyle = ort_outs


# Decode with ONNX
with torch.no_grad():
    latent = torch.tensor(exstyles[stylename]).repeat(2, 1, 1).to(device)
    latent[1, 7:18] = onnx_instyle[0, 7:18]

    print("Generating image")

    image_generation_time = datetime.now()

    exstyle = generator.generator.style(
        latent.reshape(latent.shape[0] * latent.shape[1], latent.shape[2])
    ).reshape(latent.shape)

    img_gen, _ = generator(
        [onnx_instyle.repeat(2, 1, 1)],
        exstyle,
        z_plus_latent=True,
        truncation=0.7,
        truncation_latent=0,
        use_res=True,
        interp_weights=[INTRINSIC_STYLE_WEIGHT] * 7 + [EXTRINSIC_STYLE_WEIGHT] * 11,
    )
    img_gen = torch.clamp(img_gen.detach(), -1, 1)
    print(f"Finished generating first image: {datetime.now() - image_generation_time}")

output_image: Image = Image.fromarray(
    (
        (img_gen[0, :, :, :].detach().numpy().squeeze().transpose(1, 2, 0) + 1.0)
        * 127.5
    ).astype(np.uint8),
    "RGB",
)

output_image.save("output_image_onnx.jpg")

# instyle = torch_out
# # Decode from_torch
# with torch.no_grad():
#     latent = torch.tensor(exstyles[stylename]).repeat(2, 1, 1).to(device)
#     latent[1, 7:18] = instyle[0, 7:18]

#     print("Generating image")

#     image_generation_time = datetime.now()

#     exstyle = generator.generator.style(
#         latent.reshape(latent.shape[0] * latent.shape[1], latent.shape[2])
#     ).reshape(latent.shape)

#     img_gen, _ = generator(
#         [instyle.repeat(2, 1, 1)],
#         exstyle,
#         z_plus_latent=True,
#         truncation=0.7,
#         truncation_latent=0,
#         use_res=True,
#         interp_weights=[INTRINSIC_STYLE_WEIGHT] * 7 + [EXTRINSIC_STYLE_WEIGHT] * 11,
#     )
#     img_gen = torch.clamp(img_gen.detach(), -1, 1)
#     print(
#         f"Finished generating first image: {datetime.now() - image_generation_time}"
#     )

# output_image: Image = Image.fromarray(
#     (
#         (
#             img_gen[0, :, :, :].detach().numpy().squeeze().transpose(1, 2, 0)
#             + 1.0
#         )
#         * 127.5
#     ).astype(np.uint8),
#     "RGB",
# )

# output_image.save('output_image_torch.jpg')
