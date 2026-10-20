"""
agent-hindsight: Temporal long-term memory engine with recency decay and FTS5 ranking for AI coding agents.
"""

__version__ = "0.1.0"

from .memory import retain, recall, reflect, init_db, HindsightStore

__all__ = ["retain", "recall", "reflect", "init_db", "HindsightStore"]
