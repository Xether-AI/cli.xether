import typer
from rich.console import Console
from rich.prompt import Prompt
from xether_cli.core.config import load_config, save_config, XetherConfig
from xether_cli.api.client import get_client

app = typer.Typer(help="Authentication commands")
console = Console()

@app.command()
def login():
    """Log in to the Xether AI platform"""
    config = load_config()
    
    console.print(f"[bold]Connecting to:[/bold] {config.backend_url}")
    email = Prompt.ask("Email")
    password = Prompt.ask("Password", password=True)
    
    client = get_client()
    try:
        # Real endpoint is /api/v1/auth/login
        # FastAPI OAuth2PasswordRequestForm expects x-www-form-urlencoded
        response = client.post(
            "/api/v1/auth/login", 
            data={"username": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            config.access_token = data.get("access_token")
            # Backend might not always return refresh_token in this route depending on setup
            config.refresh_token = data.get("refresh_token")
            save_config(config)
            console.print("[bold green]Successfully logged in![/bold green]")
        else:
            console.print(f"[bold red]Login failed:[/bold red] {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error connecting to server:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command()
def logout():
    """Log out of the Xether AI platform"""
    config = load_config()
    config.access_token = None
    config.refresh_token = None
    save_config(config)
    console.print("[bold green]Successfully logged out. Session cleared.[/bold green]")

@app.command()
def status():
    """Check current authentication status"""
    config = load_config()
    if not config.access_token:
        console.print("Status: [bold yellow]Not Logged In[/bold yellow]")
        return
        
    client = get_client()
    try:
        response = client.get("/api/v1/users/me")
        if response.status_code == 200:
            user = response.json()
            console.print("Status: [bold green]Logged In[/bold green]")
            console.print(f"User: [cyan]{user.get('email')}[/cyan]")
            if name := user.get('full_name'):
                console.print(f"Name: {name}")
            
            # Print team info if available
            if user_teams := user.get('teams', []):
                console.print("\n[bold]Teams:[/bold]")
                for team in user_teams:
                    role = team.get('role', 'Member')
                    team_name = team.get('team', {}).get('name', 'Unknown')
                    console.print(f"  - {team_name} ({role})")
        else:
            console.print("Status: [bold red]Session Expired or Invalid[/bold red]")
            console.print("Please run [bold]xether auth login[/bold] again.")
    except Exception as e:
        console.print(f"[bold red]Error checking status:[/bold red] {str(e)}")
    finally:
        client.close()
