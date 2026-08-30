import typer

app = typer.Typer(help="Wayfinder multi-agent trip planner.")


@app.callback()
def main() -> None:
    """Wayfinder multi-agent trip planner."""


@app.command()
def serve_tools() -> None:
    """Run the MCP tools server."""
    from wayfinder.mcp_server import main as run_server

    run_server()


@app.command()
def ask(
    question: str,
    no_tools: bool = typer.Option(
        False, "--no-tools", help="Answer without the MCP tools (Stage 1 behaviour)."
    ),
) -> None:
    """Ask the planner agent a trip question."""
    from wayfinder.planner import build_planner, mcp_client

    if no_tools:
        typer.echo(str(build_planner()(question)))
        return

    client = mcp_client()
    with client:
        agent = build_planner(tools=client.list_tools_sync())
        typer.echo(str(agent(question)))
