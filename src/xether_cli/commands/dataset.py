import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from xether_cli.api.client import get_client
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
    client = get_client()
    try:
        response = client.get(f"/api/v1/datasets?project_id={project_id}&skip={skip}&limit={limit}")
        if response.status_code == 200:
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
        else:
            console.print(f"[bold red]Failed to fetch datasets:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command("info")
def dataset_info(dataset_id: str = typer.Argument(..., help="ID of the dataset")):
    """Get detailed information about a dataset"""
    client = get_client()
    try:
        response = client.get(f"/api/v1/datasets/{dataset_id}")
        if response.status_code == 200:
            ds = response.json()
            console.print(f"[bold]Dataset Info:[/bold] {ds.get('name')}")
            for key, value in ds.items():
                console.print(f"  [bold cyan]{key}:[/bold cyan] {value}")
        else:
             console.print(f"[bold red]Failed to fetch dataset details:[/bold red] {response.status_code}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command("rm")
def remove_dataset(
    dataset_id: str = typer.Argument(..., help="ID of the dataset to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Force removal without confirmation")
):
    """Delete a dataset"""
    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete dataset {dataset_id}?")
        if not confirm:
            console.print("Operation cancelled.")
            return

    client = get_client()
    try:
        response = client.delete(f"/api/v1/datasets/{dataset_id}")
        if response.status_code == 204 or response.status_code == 200:
             console.print(f"[bold green]Dataset {dataset_id} deleted successfully.[/bold green]")
        else:
             console.print(f"[bold red]Failed to delete dataset:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
         console.print(f"[bold red]Error:[/bold red] {str(e)}")
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
    if not os.path.exists(file_path):
        console.print(f"[bold red]File not found:[/bold red] {file_path}")
        return

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    dataset_name = name or file_name
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    client = get_client()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            
            task = progress.add_task("[cyan]Registering dataset...", total=None)
            
            # Step 1: Request pre-signed URL by basically creating the dataset record in main-backend
            create_payload = {
                "name": dataset_name,
                "project_id": project_id,
                "description": description,
                "size_bytes": file_size,
                "mime_type": mime_type
            }
            
            # This is assumed to be the pattern based on Phase 2 of INTEGRATION_PLAN:
            # Backend should have an endpoint that initializes the dataset upload (or gives a presigned URL directly)
            # Assuming `/api/v1/datasets` POST creates the record and returns the upload URL
            response = client.post("/api/v1/datasets", json=create_payload)
            
            if response.status_code not in (200, 201):
                progress.stop()
                console.print(f"[bold red]Failed to register dataset:[/bold red] {response.status_code} - {response.text}")
                return
                
            dataset_info = response.json()
            upload_url = dataset_info.get("upload_url")
            dataset_id = dataset_info.get("id")
            
            if not upload_url:
                progress.stop()
                console.print(f"[bold red]Error:[/bold red] Server did not return an upload URL for dataset {dataset_id}")
                return
                
            progress.update(task, description=f"[cyan]Uploading {file_name} ({file_size} bytes)...")
            
            # Step 2: Upload bits using HTTPX directly to the pre-signed URL (MinIO/S3)
            # We don't authenticate this request typically since it's pre-signed
            import httpx
            with open(file_path, "rb") as f:
                upload_res = httpx.put(upload_url, content=f)
                
            if upload_res.status_code not in (200, 201):
                progress.stop()
                console.print(f"[bold red]Failed to upload file to storage:[/bold red] {upload_res.status_code} - {upload_res.text}")
                return
                
            # Optional: Could have a confirm upload endpoint on backend, but assume done.
            progress.stop()
            console.print(f"[bold green]Successfully uploaded {file_name}! Dataset ID: {dataset_id}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error during upload:[/bold red] {str(e)}")
    finally:
        client.close()
