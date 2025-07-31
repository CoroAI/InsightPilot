"""
Main entrypoint for the FastAPI application.

This file initializes the FastAPI app, includes API routers, and sets up core middleware and startup events.
"""

from fastapi import FastAPI

app = FastAPI(title="InsightPilot AI Agent Backend")

# Import and include routers here
# from app.api import router as api_router
# app.include_router(api_router)

# Add startup/shutdown events, middleware, etc.
