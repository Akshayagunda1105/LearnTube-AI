from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.videos import router as videos_router
from app.routes.chat import router as chat_router


app = FastAPI(
    title="LearnTube AI API",
    description="AI-powered YouTube learning assistant",
    version="1.0.0"
)


# Allow requests from our React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(videos_router)
app.include_router(chat_router)


@app.get("/")
def root():
    return {
        "message": "LearnTube AI API is running!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/api/test")
def test_connection():
    return {
        "message": "Hello from LearnTube AI backend!"
    }