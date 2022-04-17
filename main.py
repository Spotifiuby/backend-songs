import uvicorn
from fastapi import FastAPI
from docs import tags_metadata
from routes.song import song_routes
from routes.content import content_routes


app = FastAPI(
    title="Songs backend for Spotifiuby",
    description="REST API using FastAPI, MongoDB and Firebase",
    version="0.0.1",
    openapi_tags=tags_metadata
)

app.include_router(song_routes)
app.include_router(content_routes)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
