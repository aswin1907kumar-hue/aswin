from __future__ import annotations

import hashlib
import threading
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import settings


_pipeline = None
_pipeline_lock = threading.Lock()


def _safe_output_path() -> Path:
    return settings.panels_dir / f"{uuid.uuid4().hex}.png"


def _load_font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                pass
    return ImageFont.load_default()


def _demo_image(prompt: str, output: Path) -> str:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    # Deterministic neutral palette derived from the prompt.
    values = [int(digest[i:i + 2], 16) for i in (0, 2, 4, 6, 8, 10)]
    bg = tuple(35 + v // 4 for v in values[:3])
    accent = tuple(80 + v // 2 for v in values[3:])

    image = Image.new("RGB", (settings.image_width, settings.image_height), bg)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (24, 24, settings.image_width - 24, settings.image_height - 24),
        radius=28,
        outline=accent,
        width=8,
    )
    draw.ellipse(
        (
            settings.image_width * 0.25,
            settings.image_height * 0.16,
            settings.image_width * 0.75,
            settings.image_height * 0.66,
        ),
        outline=accent,
        width=8,
    )
    draw.line(
        (
            settings.image_width * 0.20,
            settings.image_height * 0.78,
            settings.image_width * 0.80,
            settings.image_height * 0.78,
        ),
        fill=accent,
        width=8,
    )
    draw.text(
        (42, settings.image_height - 105),
        "ComicCraft • Demo Illustration",
        fill=(245, 245, 245),
        font=_load_font(24),
    )
    image.save(output, format="PNG", optimize=True)
    return str(output)


def _get_pipeline():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    with _pipeline_lock:
        if _pipeline is not None:
            return _pipeline

        try:
            import torch
            from diffusers import StableDiffusionPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Diffusers image generation requires torch and diffusers. "
                "Install requirements.txt or use IMAGE_GENERATION_MODE=demo."
            ) from exc

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        kwargs = {"torch_dtype": dtype}
        if settings.hf_token:
            kwargs["token"] = settings.hf_token

        _pipeline = StableDiffusionPipeline.from_pretrained(
            settings.hf_model_id,
            **kwargs,
        )

        if settings.image_cpu_offload and torch.cuda.is_available():
            _pipeline.enable_model_cpu_offload()
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _pipeline = _pipeline.to(device)

        _pipeline.enable_attention_slicing()
        return _pipeline


def generate_image(prompt: str) -> str:
    output = _safe_output_path()

    if settings.image_generation_mode.lower() == "demo":
        return _demo_image(prompt, output)

    pipe = _get_pipeline()

    try:
        import torch

        generator = torch.Generator(
            device="cuda" if torch.cuda.is_available() else "cpu"
        ).manual_seed(settings.image_seed)

        result = pipe(
            prompt=prompt,
            negative_prompt=(
                "blurry, distorted, malformed, duplicate characters, "
                "extra limbs, unreadable text, watermark"
            ),
            width=settings.image_width,
            height=settings.image_height,
            num_inference_steps=settings.image_steps,
            guidance_scale=settings.image_guidance_scale,
            generator=generator,
        )
        result.images[0].save(output, format="PNG")
        return str(output)
    except Exception:
        if output.exists():
            output.unlink(missing_ok=True)
        raise
