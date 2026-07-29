from fastapi import FastAPI
from models import Lot

app = FastAPI()

lots: list[Lot] = []

@app.get("/")
def read_root():
    return {"message": "Lot Traceability System is running"}

@app.get("/lots")
def get_lots():
    return lots

@app.post("/lots")
def create_lot(lot: Lot):
    lots.append(lot)
    return lot

