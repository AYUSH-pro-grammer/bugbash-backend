from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import get_db, Base, engine
from routes.user import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ CORS CONFIG
origins = [
    "http://localhost:3000",  # Next.js dev
    "http://127.0.0.1:3000",

    "http://localhost:3001",  # Next.js dev
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # allowed frontend
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, etc.
    allow_headers=["*"],         # allow all headers
)

@app.get("/")
def default_route():
    return "ok"

app.include_router(user_router)