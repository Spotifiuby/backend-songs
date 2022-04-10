import uvicorn
from fastapi import FastAPI
from docs import tags_metadata
from routes.song import song_routes


app = FastAPI(
    title="Songs backend for Spotifiuby",
    description="A simple REST API using FastAPI and MongoDB",
    version="0.0.1",
    openapi_tags=tags_metadata
)

app.include_router(song_routes)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)

