"""
Litestar app entry point.
Registers controllers, configures MiniJinja template engine.
"""

from pathlib import Path

from litestar import Litestar, get
from litestar.response import Template
from litestar.contrib.minijinja import MiniJinjaTemplateEngine
from litestar.template.config import TemplateConfig

from app.controllers.enrollment_controller import EnrollmentController
from app.repositories.enrollment_repository import EnrollmentRepository

TEMPLATES_DIR = Path(__file__).parent / "templates"

_repo = EnrollmentRepository()

@get("/", name="home")
async def home() -> Template:
    stats = _repo.get_overview_stats()
    return Template("home.html", context={"stats": stats})


app = Litestar(
    route_handlers=[home, EnrollmentController],
    template_config=TemplateConfig(
        directory=TEMPLATES_DIR,
        engine=MiniJinjaTemplateEngine,
    ),
    debug=True,
)
