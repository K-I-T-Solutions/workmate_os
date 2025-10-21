import os 
from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path


# Module Imports
from app.modules.system.router import router as system_router

# ====== Basis Verzeichnis =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https;//workmate.intern.phudevelopement.xyz",
    "http://workmate_ui:5173", 
    "http://workmate.intern.phudevelopement.xyz",
    "https://login.intern.phudevelopement.xyz",
    "http://keycloak:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# === Static Files ===
UPLOAD_DIR = Path(settings.UPLOAD_DIR or (BASE_DIR + "/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
# === Module-Router ===
app.include_router(system_router, prefix="/system")

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} API online ✅"}
