from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import part_numbers, lots, users
from app.auth import router as auth_router

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
app.include_router(part_numbers.router)
app.include_router(lots.router)


@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")