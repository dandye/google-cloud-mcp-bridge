#!/usr/bin/env python3
"""Unified CLI for google-cloud-mcp-bridge.

Entrypoint for CLI commands, service operations, and development workflows.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table


# Resolve root relative to this file for cross-worktree portability
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

console = Console()

app = typer.Typer(
    name="google-cloud-mcp-bridge",
    help="Unified management CLI for google-cloud-mcp-bridge",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@app.callback()
def main_callback() -> None:
    """google-cloud-mcp-bridge CLI Operations."""
    pass


@app.command("info")
def info() -> None:
    """Display project configuration, active MCP service, and environment status."""
    active_mcp = os.getenv("ACTIVE_MCP_SERVICE", "recommender")
    gcp_project = os.getenv("GOOGLE_CLOUD_PROJECT", "(not set)")
    gcp_location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true")

    table = Table(title="Google Cloud MCP Bridge - Environment Status")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Base Directory", str(BASE_DIR))
    table.add_row("Active MCP Service", active_mcp)
    table.add_row("Google Cloud Project", gcp_project)
    table.add_row("Google Cloud Location", gcp_location)
    table.add_row("Gemini Model", model_name)
    table.add_row("Use Vertex AI", use_vertex)
    table.add_row(".env Present", str((BASE_DIR / ".env").exists()))

    console.print(table)


@app.command("chat")
def chat(
    prompt: Annotated[
        str | None,
        typer.Argument(help="User prompt to send to the ADK agent"),
    ] = None,
) -> None:
    """Execute conversational prompt against the ADK agent via test_chat.py."""
    chat_script = BASE_DIR / "scripts" / "test_chat.py"
    if not chat_script.exists():
        chat_script = BASE_DIR / "test_chat.py"
    cmd = [sys.executable, str(chat_script)]
    if prompt:
        cmd.append(prompt)
    subprocess.run(cmd, cwd=BASE_DIR, check=False)


@app.command("client")
def client() -> None:
    """Verify ADK McpToolset connection and discover tools via test_client.py."""
    client_script = BASE_DIR / "scripts" / "test_client.py"
    if not client_script.exists():
        client_script = BASE_DIR / "test_client.py"
    cmd = [sys.executable, str(client_script)]
    subprocess.run(cmd, cwd=BASE_DIR, check=False)


@app.command("serve")
def serve(
    host: Annotated[str, typer.Option("--host", "-h", help="Bind host")] = "0.0.0.0",
    port: Annotated[int, typer.Option("--port", "-p", help="Bind port")] = 8080,
    reload: Annotated[
        bool, typer.Option("--reload", "-r", help="Auto-reload on code change")
    ] = False,
) -> None:
    """Start the FastAPI agent server using Uvicorn."""
    import uvicorn

    console.print(f"[bold green]Starting Agent Server on {host}:{port}...[/bold green]")
    uvicorn.run("gcp_agent.agent:app", host=host, port=port, reload=reload)


@app.command("deploy")
def deploy() -> None:
    """Trigger agent deployment to Cloud Run / Agent Runtime via scripts/deploy.sh."""
    deploy_script = BASE_DIR / "scripts" / "deploy.sh"
    if not deploy_script.exists():
        deploy_script = BASE_DIR / "deploy.sh"
    if not deploy_script.exists():
        console.print("[red]scripts/deploy.sh not found![/red]")
        raise typer.Exit(1)
    subprocess.run([str(deploy_script)], cwd=BASE_DIR, check=False)


if __name__ == "__main__":
    app()
