from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Lot Traceability System",
    description=("Tracks manufacturing lots through the pre-sterilization lifecycle in an FDA/ISO-regulated medical device environment."),
    version="2.0.0",
)

@app.get("/", include_in_schema=False)
def read_root():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")