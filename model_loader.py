import torch
from diffusers import StableVideoDiffusionPipeline

MODEL_ID = "stabilityai/stable-video-diffusion-img2vid"

pipe = None

try:
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
    )

    pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    print("✅ Model loaded successfully")

except Exception as e:
    print("❌ Model loading failed:", e)
    pipe = None