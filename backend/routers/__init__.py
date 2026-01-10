"""APIルーター"""
from .grid import router as grid_router
from .video import router as video_router

__all__ = ['grid_router', 'video_router']
