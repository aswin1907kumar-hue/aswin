from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.schemas import ImageTestRequest, PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


router = APIRouter()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def _run_generation(request_data: PromptRequest) -> tuple[list, str]:
    outline = generate_outline(
        story_prompt=request_data.story_prompt,
        character_name=request_data.character_name,
        setting=request_data.setting,
        tone=request_data.tone,
        art_style=request_data.art_style,
    )

    story = generate_story(
        outline=outline,
        character_name=request_data.character_name,
        setting=request_data.setting,
        tone=request_data.tone,
        art_style=request_data.art_style,
    )

    image_paths = [
        generate_image(panel.image_prompt)
        for panel in story.panels
    ]

    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"settings": settings},
    )


@router.post("/generate", response_class=HTMLResponse, name="generate")
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        layout, pdf_path = _run_generation(payload)
        pdf_name = Path(pdf_path).name

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_name": pdf_name,
                "pdf_url": f"/exports/{quote(pdf_name)}",
            },
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "settings": settings,
                "error": str(exc),
                "form": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                },
            },
            status_code=500,
        )


@router.post("/generate-comic/json", response_class=JSONResponse, name="generate_json")
def generate_json(payload: PromptRequest):
    try:
        layout, pdf_path = _run_generation(payload)
        pdf_name = Path(pdf_path).name
        return {
            "success": True,
            "panel_count": len(layout),
            "layout": [panel.model_dump() for panel in layout],
            "pdf_path": f"/exports/{quote(pdf_name)}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/test-image", response_class=JSONResponse, name="test_image")
def test_image(payload: ImageTestRequest):
    try:
        path = Path(generate_image(payload.prompt))
        public_url = "/" + path.relative_to(settings.static_dir).as_posix()
        return {"success": True, "image_path": public_url}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/exports/{filename}", name="download_export")
def download_export(filename: str):
    # Only permit the generated PDF filename format.
    if "/" in filename or "\\" in filename or not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid export filename.")

    path = settings.exports_dir / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Export not found.")

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=filename,
    )


@router.get("/export-success", response_class=HTMLResponse, name="export_success")
def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )


@router.get("/health", response_class=JSONResponse, name="health")
def health():
    return {
        "status": "ok",
        "gemini_configured": bool(settings.gemini_api_key),
        "image_generation_mode": settings.image_generation_mode,
        "image_model": settings.hf_model_id
        if settings.image_generation_mode.lower() == "diffusers"
        else None,
    }
