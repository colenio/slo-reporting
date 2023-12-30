from pathlib import Path

from starlette.templating import Jinja2Templates

UI_ROOT = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(
    directory=str(UI_ROOT / "templates"),
    extensions=[
        'jinja2_time.TimeExtension'
    ]
)
