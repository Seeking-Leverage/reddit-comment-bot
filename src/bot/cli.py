import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from bot.config import load_client_config, list_client_configs
from bot.orchestrator import BotOrchestrator
from bot.settings import settings

console = Console()


@click.group()
def cli():
    """Reddit comment bot — agency client engagement tool."""


@cli.command("list-clients")
def list_clients():
    """List configured clients."""
    paths = list_client_configs(settings.bot_config_dir)
    if not paths:
        console.print("[yellow]No client configs found.[/]")
        console.print(f"Add YAML files to: {settings.bot_config_dir}")
        return

    table = Table(title="Clients")
    table.add_column("File")
    table.add_column("Client ID")
    table.add_column("Dry run")

    for path in paths:
        cfg = load_client_config(path)
        table.add_row(path.name, cfg.client_id, "yes" if cfg.dry_run else "no")

    console.print(table)


@cli.command("run")
@click.argument("client", required=False)
@click.option("--all", "run_all", is_flag=True, help="Run all configured clients.")
@click.option(
    "--live",
    is_flag=True,
    help="Post comments for real (overrides dry_run in config).",
)
def run_client(client: Optional[str], run_all: bool, live: bool):
    """Run the bot for one or all clients."""
    paths = list_client_configs(settings.bot_config_dir)
    if not paths:
        console.print("[red]No client configs found.[/]")
        sys.exit(1)

    if run_all:
        targets = paths
    elif client:
        match = settings.bot_config_dir / f"{client}.yaml"
        if not match.exists():
            match = Path(client)
        if not match.exists():
            console.print(f"[red]Client config not found: {client}[/]")
            sys.exit(1)
        targets = [match]
    else:
        console.print("[red]Provide a client name or use --all[/]")
        sys.exit(1)

    if live:
        console.print("[bold yellow]LIVE MODE — comments will be posted to Reddit[/]")

    for path in targets:
        cfg = load_client_config(path)
        if live:
            cfg = cfg.model_copy(update={"dry_run": False})

        console.print(f"\n[bold]Running {cfg.client_name}[/] ({cfg.client_id})")
        result = BotOrchestrator(cfg).run()

        console.print(
            f"Scanned {result.posts_scanned} posts · "
            f"posted {result.comments_posted} · "
            f"skipped {result.comments_skipped}"
            + (" [cyan](dry run)[/]" if result.dry_run else "")
        )


@cli.command("validate")
@click.argument("client")
def validate_client(client: str):
    """Validate a client config file."""
    path = settings.bot_config_dir / f"{client}.yaml"
    if not path.exists():
        path = Path(client)
    cfg = load_client_config(path)
    console.print(f"[green]Valid config:[/] {cfg.client_name} ({cfg.client_id})")
    console.print(f"  Focus areas: {len(cfg.focus_areas)}")
    console.print(f"  Subreddits: {sum(len(a.subreddits) for a in cfg.focus_areas)}")
    console.print(f"  Dry run: {cfg.dry_run}")


if __name__ == "__main__":
    cli()