from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.logging_config import setup_logging, get_logger
from app.routers import part_numbers, lots, users, product_families
from app.auth import router as auth_router

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Lot Traceability System",
    description=(
        "Tracks manufacturing lots through the pre-sterilization lifecycle "
        "in an FDA/ISO-regulated medical device environment."
    ),
    version="2.0.0",
)

app.include_router(auth_router.router)
app.include_router(users.router)
app.include_router(product_families.router)
app.include_router(part_numbers.router)
app.include_router(lots.router)


@app.on_event("startup")
def on_startup():
    logger.info("Application starting up")


@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")