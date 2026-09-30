# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI + Jinja2 web application that turns a user's story idea into a 5-panel comic:

1. Gemini generates a structured panel outline.
2. Gemini expands the outline into narration, captions, dialogue, and image prompts.
3. Hugging Face Diffusers generates one illustration per panel.
4. The panels are assembled into a preview layout.
5. FPDF generates a downloadable PDF.

The original project document specified Gemini Flash + Gemini Pro + Stable Diffusion. This implementation keeps that architecture but uses Google's current `google-genai` SDK and configurable current Gemini model IDs. The default text models are configurable in `.env`.

## Requirements

- Python 3.11+ recommended
- A Gemini API key
- Optional: Hugging Face access token for the image model
- For real local Stable Diffusion generation: a suitable GPU is strongly recommended
- Windows, macOS, and Linux are supported

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── comic_preview.html
│   │   └── export_success.html
│   └── static/
│       └── css/
│           └── styles.css
├── tests/
│   ├── test_layout.py
│   ├── test_schemas.py
│   └── test_app.py
├── static/
│   ├── panels/
│   └── exports/
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## 1. Open in VS Code

Open the `ComicCraft` folder in VS Code.

## 2. Create and activate a virtual environment

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
```

### macOS/Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

For a CUDA-enabled PyTorch installation, install the PyTorch build appropriate for your GPU from the official PyTorch instructions before running Diffusers.

## 4. Configure API keys

Copy `.env.example` to `.env`.

Windows:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Then set:

```env
GEMINI_API_KEY=your_key_here
HF_TOKEN=your_huggingface_token_if_needed
```

The application does not hard-code secrets.

## 5. Choose the image-generation mode

### Fastest first test: demo mode

The default `.env.example` uses:

```env
IMAGE_GENERATION_MODE=demo
```

Demo mode creates deterministic comic-style placeholder illustrations so you can verify the complete FastAPI → Gemini → layout → PDF pipeline without downloading a multi-GB diffusion model.

### Real Stable Diffusion

Set:

```env
IMAGE_GENERATION_MODE=diffusers
HF_MODEL_ID=stable-diffusion-v1-5/stable-diffusion-v1-5
```

The first real generation downloads the configured model from Hugging Face. This can require substantial disk space, RAM/VRAM, and generation time.

## 6. Run the application

```bash
uvicorn app.main:app --reload
```

Or:

```bash
python run.py
```

Open:

- http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## 7. Generate a comic

Example:

- Story prompt: `A brave fox discovers a hidden library in an enchanted forest.`
- Character: `Finn`
- Setting: `Enchanted forest`
- Tone: `dramatic`
- Art style: `anime`

Click **Create Comic**.

The app generates five panels and provides a PDF download.

## API

### POST `/generate-comic/json`

Example:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest.",
  "character_name": "Finn",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "anime"
}
```

### POST `/test-image`

```json
{
  "prompt": "A brave fox in an enchanted forest, comic illustration"
}
```

### GET `/health`

Returns application and configuration status without exposing secrets.

## Testing

Install pytest:

```bash
pip install pytest
```

Run:

```bash
pytest -q
```

The included tests cover schema validation, layout construction, health checks, and the basic web application wiring.

## Troubleshooting

### "GEMINI_API_KEY is not configured"

Set `GEMINI_API_KEY` in `.env` and restart Uvicorn.

### Image generation is too slow

Use `IMAGE_GENERATION_MODE=demo` for development, or use a suitable CUDA GPU and tune:

```env
IMAGE_STEPS=20
IMAGE_WIDTH=512
IMAGE_HEIGHT=512
```

### Out-of-memory during Diffusers generation

Use a smaller resolution/step count, enable CPU offload:

```env
IMAGE_CPU_OFFLOAD=true
```

and use a GPU with enough VRAM. The exact memory requirement depends on the model, dtype, and hardware.

### PDF cannot be generated

Make sure the generated images are readable PNG/JPEG files and that `fpdf2` is installed from `requirements.txt`.

## Security notes

- `.env` is ignored by Git.
- User input is validated with Pydantic.
- Filenames are generated by UUIDs, not raw user prompts.
- Generated export filenames are validated before download.
- The application does not expose API keys to browser JavaScript.
- AI-generated content should be reviewed before publication.
