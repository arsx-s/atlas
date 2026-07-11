"""ASGI entrypoint for Atlas backend."""

from atlas_backend.api.app import create_app

app = create_app()
