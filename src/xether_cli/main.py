import typer
from rich.console import Console

from xether_cli.commands import auth, config as config_cmd, dataset

app = typer.Typer(
    help="Xether AI Command Line Interface",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

app.add_typer(auth.app, name="auth", help="Authentication commands (login/logout)")
app.add_typer(config_cmd.app, name="config", help="Manage CLI configuration")
app.add_typer(dataset.app, name="dataset", help="Dataset management operations")

@app.command()
def info():
    """Show information about the Xether CLI"""
    console.print("[bold blue]Xether AI CLI[/bold blue] - v0.1.0")
    console.print("The official command-line interface for the Xether AI platform.")

if __name__ == "__main__":
    app()
