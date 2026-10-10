"""Web interface routes for OpenCode AI Coordinator"""

import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/web", tags=["web"])


# Get the absolute path to the web directory
WEB_DIR = Path(__file__).parent.parent / "web"
STATIC_DIR = WEB_DIR / "static"
TEMPLATES_DIR = WEB_DIR / "templates"

# Ensure directories exist
STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_class=HTMLResponse)
async def web_index(request: Request) -> HTMLResponse:
    """Serve the main web interface"""
    index_path = TEMPLATES_DIR / "index.html"
    
    if not index_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Web interface not found. Please ensure the web directory exists."
        )
    
    # Read and return the HTML file
    with open(index_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content, media_type="text/html")


@router.get("/{path:path}", response_class=HTMLResponse)
async def web_catch_all(request: Request, path: str) -> HTMLResponse:
    """Catch-all route to serve index.html for SPA routing"""
    index_path = TEMPLATES_DIR / "index.html"
    
    if not index_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Web interface not found"
        )
    
    with open(index_path, "r") as f:
        html_content = f.read()
    
    return HTMLResponse(content=html_content, media_type="text/html")


def setup_web_routes(app):
    """Setup web interface routes and static files"""
    # Include the web router
    app.include_router(router)
    
    # Mount static files
    if STATIC_DIR.exists():
        app.mount(
            "/static",
            StaticFiles(directory=str(STATIC_DIR)),
            name="static"
        )
    
    # Also serve static files from /web/static for direct access
    web_static_dir = WEB_DIR / "static"
    if web_static_dir.exists():
        app.mount(
            "/web/static",
            StaticFiles(directory=str(web_static_dir)),
            name="web_static"
        )
