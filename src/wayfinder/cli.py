import typer

app = typer.Typer(help="Wayfinder multi-agent trip planner.")


@app.callback()
def main() -> None:
    """Wayfinder multi-agent trip planner."""
    # Without a callback Typer collapses a single-command app, so `wayfinder ask
    # "..."` would parse `ask` as the question.


@app.command()
def ask(question: str) -> None:
    """Ask the planner agent a trip question."""
    from wayfinder.planner import build_planner

    typer.echo(str(build_planner()(question)))
