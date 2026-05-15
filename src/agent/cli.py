"""Local CLI — ``agent chat`` for terminal-based iteration."""

from __future__ import annotations

import sys

import typer
from rich.console import Console
from rich.panel import Panel

from agent import __version__
from agent.agent import Agent
from agent.config import Settings
from agent.memory import Memory

app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def chat(
    model_id: str | None = typer.Option(None, help="Override BEDROCK_MODEL_ID."),
    session: str | None = typer.Option(None, help="Resume a session id."),
) -> None:
    """Interactive chat with the agent (Ctrl-D to exit)."""
    settings = Settings.from_env()
    if model_id:
        settings = Settings(**{**settings.__dict__, "model_id": model_id})

    memory = Memory.from_env(settings)
    agent = Agent(settings=settings, memory=memory)

    console.print(
        Panel.fit(
            f"[bold]bedrock-agent-starter[/bold] v{__version__}\n"
            f"model: [cyan]{settings.model_id}[/cyan]\n"
            f"region: [cyan]{settings.region}[/cyan]\n"
            f"memory: [cyan]{settings.memory_backend}[/cyan]\n\n"
            "Type messages, Ctrl-D to exit.",
            border_style="magenta",
        )
    )

    current_session = session
    while True:
        try:
            user = console.input("[bold green]>[/bold green] ").strip()
        except EOFError:
            console.print("\n[dim]bye.[/dim]")
            return
        if not user:
            continue

        result = agent.run(user, session_id=current_session)
        current_session = result.session_id
        console.print(result.output_text)
        if result.tool_calls:
            console.print(
                f"[dim]· {result.turns} turn(s), tools: {', '.join(result.tool_calls)}, "
                f"{result.input_tokens} in / {result.output_tokens} out, "
                f"{result.duration_ms} ms[/dim]"
            )
        else:
            console.print(
                f"[dim]· {result.input_tokens} in / {result.output_tokens} out, "
                f"{result.duration_ms} ms[/dim]"
            )


def main() -> None:
    """Entry point for the ``agent`` script."""
    try:
        app()
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
