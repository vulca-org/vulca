"""Skill marketplace API routers."""

from app.prototype.skills.api.skill_routes import skill_api_router
from app.prototype.skills.api.discussion_routes import discussion_router
from app.prototype.skills.api.version_routes import version_router

__all__ = ["skill_api_router", "discussion_router", "version_router"]
