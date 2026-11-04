import typer
import uvicorn

from .db import init_db

app = typer.Typer()
sites_app = typer.Typer(help="Manage manual sites (coming in Phase 1).")
app.add_typer(sites_app, name="sites")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Run the StudyForge web app."""
    uvicorn.run("studyforge.app:app", host=host, port=port)


@app.command()
def initdb() -> None:
    """Create the SQLite database and all tables."""
    engine = init_db()
    typer.echo(f"Database initialized: {engine.url}")
