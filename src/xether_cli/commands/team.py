"""Team management commands for Xether AI CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from xether_cli.api.client import XetherAPIClient

app = typer.Typer(help="Team management and collaboration")
console = Console()


@app.command()
def list():
    """List teams you are a member of."""
    client = XetherAPIClient()
    
    try:
        response = client.get("/teams/")
        response.raise_for_status()
        teams = response.json()
        
        if not teams:
            console.print("[yellow]No teams found.[/yellow]")
            return
        
        table = Table(title="Teams")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Owner ID", style="blue")
        table.add_column("Created", style="dim")
        
        for team in teams:
            table.add_row(
                str(team["id"]),
                team["name"],
                team.get("description", "N/A"),
                str(team["owner_id"]),
                team.get("created_at", "N/A")[:19] if team.get("created_at") else "N/A"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing teams: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    team_id: int = typer.Argument(..., help="Team ID to view"),
):
    """Show detailed information about a specific team."""
    client = XetherAPIClient()
    
    try:
        response = client.get(f"/teams/{team_id}")
        response.raise_for_status()
        team = response.json()
        
        panel_content = f"""
[bold cyan]ID:[/bold cyan] {team["id"]}
[bold magenta]Name:[/bold magenta] {team["name"]}
[bold green]Description:[/bold green] {team.get("description", "N/A")}
[bold blue]Owner ID:[/bold blue] {team["owner_id"]}
[bold yellow]Created:[/bold yellow] {team.get("created_at", "N/A")}
[bold yellow]Updated:[/bold yellow] {team.get("updated_at", "N/A")}
        """.strip()
        
        console.print(Panel(panel_content, title=f"Team Details: {team['name']}"))
        
    except Exception as e:
        console.print(f"[red]Error fetching team info: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Team name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Team description"),
):
    """Create a new team."""
    client = XetherAPIClient()
    
    team_data = {
        "name": name,
    }
    
    if description:
        team_data["description"] = description
    
    try:
        response = client.post("/teams/", json=team_data)
        response.raise_for_status()
        team = response.json()
        
        console.print(f"[green]✓[/green] Team '{team['name']}' created successfully!")
        console.print(f"[cyan]Team ID:[/cyan] {team['id']}")
        console.print(f"[blue]Owner ID:[/blue] {team['owner_id']}")
        
    except Exception as e:
        console.print(f"[red]Error creating team: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
    team_id: int = typer.Argument(..., help="Team ID to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New team name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New team description"),
):
    """Update team details."""
    if not name and not description:
        console.print("[red]Error: At least one field to update must be provided[/red]")
        raise typer.Exit(1)
    
    client = XetherAPIClient()
    
    update_data = {}
    if name:
        update_data["name"] = name
    if description is not None:  # Allow empty string to clear description
        update_data["description"] = description
    
    try:
        response = client.patch(f"/teams/{team_id}", json=update_data)
        response.raise_for_status()
        team = response.json()
        
        console.print(f"[green]✓[/green] Team '{team['name']}' updated successfully!")
        
    except Exception as e:
        console.print(f"[red]Error updating team: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def members(
    team_id: int = typer.Argument(..., help="Team ID to view members"),
):
    """List all members of a team."""
    client = XetherAPIClient()
    
    try:
        response = client.get(f"/teams/{team_id}/members")
        response.raise_for_status()
        members = response.json()
        
        if not members:
            console.print(f"[yellow]No members found for team {team_id}.[/yellow]")
            return
        
        table = Table(title=f"Team {team_id} Members")
        table.add_column("User ID", style="cyan", no_wrap=True)
        table.add_column("Email", style="magenta")
        table.add_column("Role", style="green")
        table.add_column("Joined", style="dim")
        
        for member in members:
            table.add_row(
                str(member["user_id"]),
                member.get("email", "N/A"),
                member["role"],
                member.get("created_at", "N/A")[:19] if member.get("created_at") else "N/A"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing team members: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def add_member(
    team_id: int = typer.Argument(..., help="Team ID"),
    user_id: int = typer.Option(..., "--user", "-u", help="User ID to add"),
    role: str = typer.Option("member", "--role", "-r", help="Role (admin, manager, developer, viewer)"),
):
    """Add a member to a team."""
    if role not in ["admin", "manager", "developer", "viewer"]:
        console.print("[red]Error: Role must be one of: admin, manager, developer, viewer[/red]")
        raise typer.Exit(1)
    
    client = XetherAPIClient()
    
    member_data = {
        "user_id": user_id,
        "role": role
    }
    
    try:
        response = client.post(f"/teams/{team_id}/members", json=member_data)
        response.raise_for_status()
        
        console.print(f"[green]✓[/green] User {user_id} added to team {team_id} as {role}!")
        
    except Exception as e:
        console.print(f"[red]Error adding team member: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def remove_member(
    team_id: int = typer.Argument(..., help="Team ID"),
    user_id: int = typer.Option(..., "--user", "-u", help="User ID to remove"),
):
    """Remove a member from a team."""
    client = XetherAPIClient()
    
    try:
        response = client.delete(f"/teams/{team_id}/members/{user_id}")
        response.raise_for_status()
        
        console.print(f"[green]✓[/green] User {user_id} removed from team {team_id}!")
        
    except Exception as e:
        console.print(f"[red]Error removing team member: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    team_id: int = typer.Argument(..., help="Team ID to delete"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation prompt"),
):
    """Delete a team (owner only)."""
    if not confirm:
        console.print(f"[yellow]Warning: This will permanently delete team {team_id}[/yellow]")
        if not typer.confirm("Are you sure you want to continue?"):
            console.print("Operation cancelled.")
            raise typer.Exit()
    
    client = XetherAPIClient()
    
    try:
        response = client.delete(f"/teams/{team_id}")
        response.raise_for_status()
        
        console.print(f"[green]✓[/green] Team {team_id} deleted successfully!")
        
    except Exception as e:
        console.print(f"[red]Error deleting team: {e}[/red]")
        raise typer.Exit(1)
