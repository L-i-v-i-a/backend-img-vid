import torch
from diffusers import StableVideoDiffusionPipeline

MODEL_ID = "stabilityai/stable-video-diffusion-img2vid"

pipe = None


def load_pipe():
    global pipe

    if pipe is not None:
        return pipe

    print("🚀 Loading model...")

    try:
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float32  # safer for Render CPU
        )

        device = "cuda" if torch.cuda.is_available() else "cpu"
        pipe.to(device)

        # reduce memory usage (VERY IMPORTANT)
        pipe.enable_attention_slicing()

        print("✅ Model loaded successfully")

    except Exception as e:
        print("❌ Model loading failed:", e)
        pipe = None

    return pipe