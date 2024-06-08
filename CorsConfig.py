from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
        "http://localhost:8080" # backend port
]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True, # cookie setting
        allow_methods=["POST", "GET", "DELETE", "PUT", "PATCH", "OPTIONS"],
        allow_headers=["*"],
)