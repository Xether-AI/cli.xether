import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from xether_cli.api.client import get_client, XetherNetworkError, XetherHTTPError, XetherAuthError
from xether_cli.core.validation import validate_file_path, validate_project_id, validate_dataset_name, validate_resource_id
import os
import mimetypes

app = typer.Typer(help="Dataset management commands")
console = Console()

@app.command("ls")
def list_datasets(
    project_id: int = typer.Option(..., "--project-id", "-p", help="ID of the project"),
    skip: int = typer.Option(0, help="Skip N datasets"),
    limit: int = typer.Option(50, help="Limit number of returned datasets")
):
    """List available datasets"""
    # Validate inputs
    project_id = validate_project_id(str(project_id))
    
    client = get_client()
    try:
        response = client.get(f"/api/v1/datasets?project_id={project_id}&skip={skip}&limit={limit}")
        datasets = response.json()
        if not datasets:
            console.print("No datasets found.")
            return
            
        table = Table(title="Xether Datasets")
        table.add_column("ID", justify="left", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Size (Bytes)", justify="right", style="green")
        table.add_column("Created At", justify="right", style="blue")
        
        for ds in datasets:
            table.add_row(
                str(ds.get("id", "")),
                ds.get("name", "Unnamed"),
                str(ds.get("size_bytes", 0)),
                ds.get("created_at", "")[:10]
            )
        console.print(table)
    except XetherNetworkError as e:
        console.print(f"[bold red]Network error:[/bold red] {e}")
    except XetherHTTPError as e:
        console.print(f"[bold red]HTTP error {e.status_code}:[/bold red] {e}")
    except XetherAuthError as e:
        console.print(f"[bold red]Authentication error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
    finally:
        client.close()

@app.command("info")
def dataset_info(dataset_id: str = typer.Argument(..., help="ID of the dataset")):
    """Get detailed information about a dataset"""
    # Validate input
    dataset_id = validate_resource_id(dataset_id, "dataset")
    
    client = get_client()
    try:
        response = client.get(f"/api/v1/datasets/{dataset_id}")
        ds = response.json()
        console.print(f"[bold]Dataset Info:[/bold] {ds.get('name')}")
        for key, value in ds.items():
            console.print(f"  [bold cyan]{key}:[/bold cyan] {value}")
    except XetherNetworkError as e:
        console.print(f"[bold red]Network error:[/bold red] {e}")
    except XetherHTTPError as e:
        console.print(f"[bold red]HTTP error {e.status_code}:[/bold red] {e}")
    except XetherAuthError as e:
        console.print(f"[bold red]Authentication error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
    finally:
        client.close()

@app.command("rm")
def remove_dataset(
    dataset_id: str = typer.Argument(..., help="ID of the dataset to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation")
):
    """Delete a dataset"""
    # Validate input
    dataset_id = validate_resource_id(dataset_id, "dataset")
    
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete dataset {dataset_id}?")
        if not confirm:
            console.print("Operation cancelled.")
            return

    client = get_client()
    try:
        response = client.delete(f"/api/v1/datasets/{dataset_id}")
        console.print(f"[bold green]Dataset {dataset_id} deleted successfully.[/bold green]")
    except XetherNetworkError as e:
        console.print(f"[bold red]Network error:[/bold red] {e}")
    except XetherHTTPError as e:
        console.print(f"[bold red]HTTP error {e.status_code}:[/bold red] {e}")
    except XetherAuthError as e:
        console.print(f"[bold red]Authentication error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
    finally:
        client.close()

@app.command("push")
def push_dataset(
    file_path: str = typer.Argument(..., help="Path to the local file to upload"),
    project_id: int = typer.Option(..., "--project-id", "-p", help="ID of the project"),
    name: str = typer.Option(None, help="Name for the dataset (defaults to file name)"),
    description: str = typer.Option("", help="Optional description")
):
    """Upload a new dataset"""
    # Validate inputs
    file_path = validate_file_path(file_path, must_exist=True, must_be_file=True)
    project_id = validate_project_id(str(project_id))
    name = validate_dataset_name(name or Path(file_path).name)
    
    client = get_client()
    try:
        # Step 1: Request pre-signed upload URL
        upload_data = {
            "filename": Path(file_path).name,
            "size_bytes": Path(file_path).stat().st_size,
            "mime_type": mimetypes.guess_type(file_path)[0] or "application/octet-stream",
            "project_id": project_id,
            "name": name,
            "description": description
        }
        
        response = client.post("/api/v1/datasets/upload-url", json=upload_data)
        upload_info = response.json()
        
        # Step 2: Upload file to storage
        upload_url = upload_info["upload_url"]
        dataset_id = upload_info["dataset_id"]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan]Uploading {Path(file_path).name}...", total=None)
            
            # Step 2: Upload file to storage
            import httpx
            with open(file_path, "rb") as f:
                upload_response = httpx.put(upload_url, content=f)
                if upload_response.status_code not in (200, 201):
                    raise Exception(f"Upload failed: {upload_response.text}")
        
        console.print(f"[bold green]Successfully uploaded dataset![/bold green]")
        console.print(f"Dataset ID: [bold cyan]{dataset_id}[/bold cyan]")
        
    except XetherNetworkError as e:
        console.print(f"[bold red]Network error:[/bold red] {e}")
    except XetherHTTPError as e:
        console.print(f"[bold red]HTTP error {e.status_code}:[/bold red] {e}")
    except XetherAuthError as e:
        console.print(f"[bold red]Authentication error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    finally:
        client.close()
