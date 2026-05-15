import torch
import imageio
from PIL import Image

from model_loader import pipe


def generate_video(
    image_path: str,
    motion: str = "zoom",
    frames: int = 8,
    output_path: str = "outputs/generated.mp4"
):

    image = Image.open(image_path).convert("RGB")

    # Seed for reproducibility
    generator = torch.manual_seed(42)

    # =========================
    # AI PIPELINE CALL
    # =========================
    result = pipe(
        image,
        decode_chunk_size=1,
        num_frames=frames,
        generator=generator
    )

    frames_output = result.frames[0]

    imageio.mimsave(
        output_path,
        frames_output,
        fps=7
    )

    return output_path