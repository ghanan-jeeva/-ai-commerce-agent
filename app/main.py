from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import endpoints

app = FastAPI(
    title="AI Commerce Agent",
    description="AI-powered commerce assistant with hybrid search capabilities",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Commerce Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include router
app.include_router(
    endpoints.router,
    prefix="/api",
    tags=["search"]
) 