import typer
from rich.console import Console
from rich.table import Table
from xether_cli.api.client import get_client

app = typer.Typer(help="Pipeline orchestration commands")
console = Console()

@app.command("ls")
def list_pipelines(
    skip: int = typer.Option(0, help="Skip N pipelines"),
    limit: int = typer.Option(50, help="Limit number of returned pipelines")
):
    """List available pipelines"""
    client = get_client()
    try:
        response = client.get(f"/api/v1/pipelines?skip={skip}&limit={limit}")
        if response.status_code == 200:
            pipelines = response.json()
            if not pipelines:
                console.print("No pipelines found.")
                return
                
            table = Table(title="Xether Pipelines")
            table.add_column("ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Status", justify="right", style="green")
            table.add_column("Created At", justify="right", style="blue")
            
            for p in pipelines:
                table.add_row(
                    str(p.get("id", "")),
                    p.get("name", "Unnamed"),
                    p.get("status", "UNKNOWN"),
                    p.get("created_at", "")[:10]
                )
            console.print(table)
        else:
            console.print(f"[bold red]Failed to fetch pipelines:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command("run")
def run_pipeline(
    pipeline_id: str = typer.Argument(..., help="ID of the pipeline to trigger"),
    dataset_id: str = typer.Option(..., "--dataset", "-d", help="ID of the dataset to process")
):
    """Trigger a new pipeline execution"""
    client = get_client()
    try:
        payload = {"dataset_id": dataset_id}
        response = client.post(f"/api/v1/pipelines/{pipeline_id}/executions", json=payload)
        
        if response.status_code in (200, 201, 202):
            exec_data = response.json()
            exec_id = exec_data.get("id")
            console.print(f"[bold green]Successfully triggered pipeline![/bold green]")
            console.print(f"Execution ID: [bold cyan]{exec_id}[/bold cyan]")
            console.print(f"Check status with: [bold]xether pipeline status {exec_id}[/bold]")
        else:
            console.print(f"[bold red]Failed to trigger pipeline:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command("status")
def pipeline_status(
    execution_id: str = typer.Argument(..., help="ID of the execution to check")
):
    """Check the real-time status of a pipeline run"""
    client = get_client()
    try:
        response = client.get(f"/api/v1/executions/{execution_id}")
        if response.status_code == 200:
            exec_data = response.json()
            status = exec_data.get("status", "UNKNOWN")
            
            color = "cyan"
            if status == "COMPLETED" or status == "SUCCESS": color = "green"
            elif status == "FAILED" or status == "ERROR": color = "red"
            elif status == "RUNNING" or status == "IN_PROGRESS": color = "yellow"
            
            console.print(f"Execution [bold]{execution_id}[/bold] status: [bold {color}]{status}[/bold {color}]")
            
            # Print logs or output artifacts if any
            if error := exec_data.get("error_message"):
                 console.print(f"[bold red]Error Details:[/bold red] {error}")
                 
            if artifacts := exec_data.get("artifacts"):
                 console.print("\n[bold]Generated Artifacts:[/bold]")
                 for a in artifacts:
                     console.print(f"  - {a.get('id')} ({a.get('name')})")
        else:
            console.print(f"[bold red]Failed to fetch status:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()

@app.command("history")
def pipeline_history(
    pipeline_id: str = typer.Argument(..., help="ID of the pipeline to view history for")
):
    """List previous executions of a specific pipeline"""
    client = get_client()
    try:
        response = client.get(f"/api/v1/pipelines/{pipeline_id}/executions")
        if response.status_code == 200:
            executions = response.json()
            if not executions:
                console.print(f"No executions found for pipeline {pipeline_id}.")
                return
                
            table = Table(title=f"Execution History ({pipeline_id})")
            table.add_column("Exec ID", justify="left", style="cyan", no_wrap=True)
            table.add_column("Status", justify="right", style="magenta")
            table.add_column("Started At", justify="right", style="blue")
            table.add_column("Completed At", justify="right", style="green")
            
            for ex in executions:
                table.add_row(
                    str(ex.get("id", "")),
                    ex.get("status", "UNKNOWN"),
                    ex.get("started_at", "")[:19] if ex.get("started_at") else "-",
                    ex.get("completed_at", "")[:19] if ex.get("completed_at") else "-"
                )
            console.print(table)
        else:
            console.print(f"[bold red]Failed to fetch history:[/bold red] {response.status_code} - {response.text}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    finally:
        client.close()
