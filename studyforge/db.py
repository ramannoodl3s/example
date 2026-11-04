from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import get_settings
from .models import Base


def get_engine(db_path: str | None = None) -> Engine:
    path = Path(db_path or get_settings().db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}")


def init_db(db_path: str | None = None) -> Engine:
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine
