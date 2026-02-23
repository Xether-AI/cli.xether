import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, DownloadColumn, TextColumn, TimeRemainingColumn
from xether_cli.api.client import get_client
import os

app = typer.Typer(help="Artifact operations")
console = Console()

@app.command("ls")
def list_artifacts(
    execution_id: str = typer.Option(None, "--execution", "-e", help="Filter by Pipeline Execution ID"),
    skip: int = typer.Option(0, help="Skip N artifacts"),
    limit: int = typer.Option(50, help="Limit number of returned artifacts")
):
    """List available artifacts"""
    client = get_client()
    try:
        url = f"/api/v1/artifacts?skip={skip}&limit={limit}"
        if execution_id:
             url += f"&execution_id={execution_id}"
             
        response = client.get(url)
        if response.status_code == 200:
            artifacts = response.json()
            if not artifacts:
                console.print("No artifacts found.")
                return
                
            table = Table(title="Xether Artifacts")
            table.add_column("ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Type", style="yellow")
            table.add_column("Size (Bytes)", justify="right", style="green")
            table.add_column("Created At", justify="right", style="blue")
            
            for art in artifacts:
                table.add_row(
                    str(art.get("id", "")),
                    art.get("name", "Unnamed"),
                    art.get("artifact_type", "UNKNOWN"),
                    str(art.get("size_bytes", 0)),
                    art.get("created_at", "")[:10]
                )
            console.print(table)
        else:
            console.print(f"[bold red]Failed to fetch artifacts:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command("download")
def download_artifact(
    artifact_id: str = typer.Argument(..., help="ID of the artifact to download"),
    destination: str = typer.Argument(..., help="Destination dir or file path")
):
    """Download an artifact"""
    client = get_client()
    try:
        # Step 1: Request pre-signed download URL from Backend
        response = client.get(f"/api/v1/artifacts/{artifact_id}/download-url")
        if response.status_code != 200:
            console.print(f"[bold red]Failed to get download URL:[/bold red] {response.status_code} - {response.text}")
            return
            
        data = response.json()
        download_url = data.get("download_url")
        artifact_name = data.get("name", f"artifact_{artifact_id}")
        
        # Step 2: Determine full destination path
        if os.path.isdir(destination):
            dest_path = os.path.join(destination, artifact_name)
        else:
             # Assume given path is a file or in a directory we can write to
            dest_path = destination

        # Step 3: Stream download using HTTPX directly with a rich progress bar
        import httpx
        with httpx.stream("GET", download_url) as r:
            if r.status_code != 200:
                 console.print(f"[bold red]Storage error fetching file:[/bold red] {r.status_code}")
                 return
                 
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                DownloadColumn(),
                TimeRemainingColumn(),
                transient=True,
            ) as progress:
                
                task = progress.add_task(f"[cyan]Downloading {artifact_name}...", total=total_size_in_bytes)
                
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_bytes(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
                            
        console.print(f"[bold green]Successfully downloaded artifact to[/bold green] [cyan]{dest_path}[/cyan]")
        
    except httpx.RequestError as exc:
        console.print(f"[bold red]Network error during download:[/bold red] {exc}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()
