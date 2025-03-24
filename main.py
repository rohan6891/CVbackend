from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn

#routes imports
from routes.auth import router as auth_router
from routes.resume import router as resume_router
from routes.report import router as report_router
from routes.questions import router as questions_router

app = FastAPI()

# Load environment variables from .env file
load_dotenv()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix="/auth")
app.include_router(resume_router, prefix="/resume")
app.include_router(questions_router, prefix="/questions")
app.include_router(report_router, prefix="/report")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)