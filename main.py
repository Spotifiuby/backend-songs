import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from docs import tags_metadata
from logging.config import dictConfig
from config.log_conf import log_config

from routes.song import song_routes
from routes.content import content_routes
from routes.artist import artist_routes
from routes.album import album_routes
from routes.playlist import playlist_routes


dictConfig(log_config)
app = FastAPI(
    title="Songs backend for Spotifiuby",
    description="REST API using FastAPI, MongoDB and Firebase",
    version="0.0.1",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)


# TODO: En producción no se podría dejar así
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(song_routes)
app.include_router(content_routes)
app.include_router(artist_routes)
app.include_router(album_routes)
app.include_router(playlist_routes)


@app.get("/", include_in_schema=False)
def ping():
    return Response(status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
