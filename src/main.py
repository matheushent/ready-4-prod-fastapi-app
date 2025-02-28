"""Main module for the API."""

import toml
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from src.graphql_app import graphql_router

version = toml.load("pyproject.toml").get("tool").get("poetry").get("version")

app = FastAPI(version=version, title="Finance API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_router, tags=["GraphQL"])


@app.get(
    "/health",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={204: {"description": "API is healthy"}},
)
async def health():  # noqa: D103
    return Response(status_code=status.HTTP_204_NO_CONTENT)
