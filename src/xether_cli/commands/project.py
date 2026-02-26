"""Project management commands for Xether AI CLI."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Optional

from xether_cli.api.client import XetherAPIClient

app = typer.Typer(help="Project workspace management")
console = Console()


@app.command()
def list(
    team_id: Optional[int] = typer.Option(None, "--team", "-t", help="Filter by team ID"),
):
    """List projects you have access to."""
    client = XetherAPIClient()
    
    params = {}
    if team_id:
        params["team_id"] = team_id
    
    try:
        response = client.get("/projects/", params=params)
        response.raise_for_status()
        projects = response.json()
        
        if not projects:
            console.print("[yellow]No projects found.[/yellow]")
            return
        
        table = Table(title="Projects")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Description", style="green")
        table.add_column("Team ID", style="blue")
        table.add_column("Created", style="dim")
        
        for project in projects:
            table.add_row(
                str(project["id"]),
                project["name"],
                project.get("description", "N/A"),
                str(project["team_id"]),
                project.get("created_at", "N/A")[:19] if project.get("created_at") else "N/A"
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing projects: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info(
    project_id: int = typer.Argument(..., help="Project ID to view"),
):
    """Show detailed information about a specific project."""
    client = XetherAPIClient()
    
    try:
        response = client.get(f"/projects/{project_id}")
        response.raise_for_status()
        project = response.json()
        
        panel_content = f"""
[bold cyan]ID:[/bold cyan] {project["id"]}
[bold magenta]Name:[/bold magenta] {project["name"]}
[bold green]Description:[/bold green] {project.get("description", "N/A")}
[bold blue]Team ID:[/bold blue] {project["team_id"]}
[bold yellow]Created:[/bold yellow] {project.get("created_at", "N/A")}
[bold yellow]Updated:[/bold yellow] {project.get("updated_at", "N/A")}
        """.strip()
        
        console.print(Panel(panel_content, title=f"Project Details: {project['name']}"))
        
    except Exception as e:
        console.print(f"[red]Error fetching project info: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    team_id: int = typer.Option(..., "--team", "-t", help="Team ID to create project in"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Project description"),
):
    """Create a new project in a team."""
    client = XetherAPIClient()
    
    project_data = {
        "name": name,
        "team_id": team_id,
    }
    
    if description:
        project_data["description"] = description
    
    try:
        response = client.post("/projects/", json=project_data)
        response.raise_for_status()
        project = response.json()
        
        console.print(f"[green]✓[/green] Project '{project['name']}' created successfully!")
        console.print(f"[cyan]Project ID:[/cyan] {project['id']}")
        console.print(f"[blue]Team ID:[/blue] {project['team_id']}")
        
    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def update(
    project_id: int = typer.Argument(..., help="Project ID to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New project name"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New project description"),
):
    """Update project details."""
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
        response = client.patch(f"/projects/{project_id}", json=update_data)
        response.raise_for_status()
        project = response.json()
        
        console.print(f"[green]✓[/green] Project '{project['name']}' updated successfully!")
        
    except Exception as e:
        console.print(f"[red]Error updating project: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def delete(
    project_id: int = typer.Argument(..., help="Project ID to delete"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation prompt"),
):
    """Delete a project (admin only)."""
    if not confirm:
        console.print(f"[yellow]Warning: This will permanently delete project {project_id}[/yellow]")
        if not typer.confirm("Are you sure you want to continue?"):
            console.print("Operation cancelled.")
            raise typer.Exit()
    
    client = XetherAPIClient()
    
    try:
        response = client.delete(f"/projects/{project_id}")
        response.raise_for_status()
        
        console.print(f"[green]✓[/green] Project {project_id} deleted successfully!")
        
    except Exception as e:
        console.print(f"[red]Error deleting project: {e}[/red]")
        raise typer.Exit(1)
