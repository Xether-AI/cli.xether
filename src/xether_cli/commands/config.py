import typer
from rich.console import Console
from xether_cli.core.config import load_config, save_config

app = typer.Typer(help="Configuration commands")
console = Console()

@app.command()
def view():
    """View current CLI configuration"""
    config = load_config()
    console.print("[bold]Current Configuration:[/bold]")
    console.print(f"Backend URL: {config.backend_url}")
    if config.access_token:
        console.print("Status: [bold green]Logged In[/bold green]")
    else:
        console.print("Status: [bold yellow]Not Logged In[/bold yellow]")

@app.command()
def set(
    backend_url: str = typer.Option(None, "--backend-url", "-b", help="Set the Backend API URL")
):
    """Update CLI configuration"""
    config = load_config()
    changed = False
    
    if backend_url:
        config.backend_url = backend_url
        changed = True
        console.print(f"Set backend URL to: [bold]{backend_url}[/bold]")
        
    if changed:
        save_config(config)
        console.print("[bold green]Configuration updated successfully.[/bold green]")
    else:
        console.print("No changes made. Use options like --backend-url to update config.")
