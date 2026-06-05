"""Main CLI application for iq."""

import typer
from typing import Optional
from typing_extensions import Annotated

from .auth import auth_manager
from .client import client
from .config import config
from .formatters import (
    format_output,
    print_success,
    print_error,
    print_warning,
    print_info
)

app = typer.Typer(
    name="iq",
    help="CLI tool to interact with iquall system",
    add_completion=False
)

# Create subcommands
get_app = typer.Typer(help="Get resources from iquall")
create_app = typer.Typer(help="Create resources in iquall")
delete_app = typer.Typer(help="Delete resources from iquall")
run_app = typer.Typer(help="Run jobs in iquall")
config_app = typer.Typer(help="Configure iq CLI")

app.add_typer(get_app, name="get")
app.add_typer(create_app, name="create")
app.add_typer(delete_app, name="delete")
app.add_typer(run_app, name="run")
app.add_typer(config_app, name="config")


# Authentication commands
@app.command()
def login(
    email: Annotated[Optional[str], typer.Option("--email", "-e", help="User email")] = None,
    password: Annotated[Optional[str], typer.Option("--password", "-p", help="User password")] = None,
):
    """Authenticate with iquall system."""
    if not email:
        email = typer.prompt("Email")
    if not password:
        password = typer.prompt("Password", hide_input=True)

    print_info(f"Authenticating as {email}...")

    if auth_manager.login(email, password):
        print_success("Successfully authenticated!")
    else:
        print_error("Authentication failed. Please check your credentials.")
        raise typer.Exit(1)


@app.command()
def logout():
    """Remove stored credentials."""
    if auth_manager.is_authenticated():
        auth_manager.logout()
        print_success("Successfully logged out!")
    else:
        print_warning("Not currently authenticated.")


# Get commands
@get_app.command("sandboxes")
def get_sandboxes(
    name: Annotated[Optional[str], typer.Option("--name", "-n", help="Filter by sandbox name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Get list of sandboxes."""
    try:
        result = client.get_sandboxes(sandbox_name=name)
        format_output(result, output, "Sandboxes")
    except Exception as e:
        print_error(f"Failed to get sandboxes: {e}")
        raise typer.Exit(1)


@get_app.command("deployment")
def get_deployment(
    environment: Annotated[Optional[str], typer.Option("--environment", "-e", help="Environment name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Get deployment information."""
    try:
        result = client.get_deployment(environment=environment)
        format_output(result, output, "Deployment")
    except Exception as e:
        print_error(f"Failed to get deployment: {e}")
        raise typer.Exit(1)


@get_app.command("network-task")
def get_network_task(
    instance_id: Annotated[str, typer.Argument(help="Network task instance ID")],
    environment: Annotated[Optional[str], typer.Option("--environment", "-e", help="Environment name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Get network task details."""
    try:
        result = client.get_network_task(instance_id, environment=environment)
        format_output(result, output, f"Network Task: {instance_id}")
    except Exception as e:
        print_error(f"Failed to get network task: {e}")
        raise typer.Exit(1)


@get_app.command("job")
def get_job(
    job_id: Annotated[str, typer.Argument(help="Job ID")],
    environment: Annotated[Optional[str], typer.Option("--environment", "-e", help="Environment name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Get job status."""
    try:
        result = client.get_job_status(job_id, environment=environment)
        format_output(result, output, f"Job: {job_id}")
    except Exception as e:
        print_error(f"Failed to get job: {e}")
        raise typer.Exit(1)


@get_app.command("jobs")
def get_jobs(
    instance_id: Annotated[Optional[str], typer.Option("--instance-id", "-i", help="Filter by instance ID")] = None,
    app_id: Annotated[Optional[str], typer.Option("--app-id", "-a", help="Filter by app ID")] = None,
    first: Annotated[int, typer.Option("--first", "-n", help="Number of jobs to return")] = 10,
    order: Annotated[str, typer.Option("--order", help="Sort order for execution_date (asc/desc)")] = "desc",
    after: Annotated[Optional[str], typer.Option("--after", help="Cursor for pagination (after)")] = None,
    before: Annotated[Optional[str], typer.Option("--before", help="Cursor for pagination (before)")] = None,
    environment: Annotated[Optional[str], typer.Option("--environment", "-e", help="Environment name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Get list of jobs with optional filters."""
    try:
        result = client.get_jobs_with_filter(
            first=first,
            instance_id=instance_id,
            app_id=app_id,
            order_by=order,
            before=before,
            after=after,
            environment=environment
        )
        format_output(result, output, "Jobs")
    except Exception as e:
        print_error(f"Failed to get jobs: {e}")
        raise typer.Exit(1)


# Create commands
@create_app.command("sandbox")
def create_sandbox(
    name: Annotated[str, typer.Argument(help="Sandbox name")],
    flavor: Annotated[str, typer.Option("--flavor", "-f", help="Sandbox flavor (FULL, etc.)")] = "FULL",
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Create a new sandbox."""
    try:
        print_info(f"Creating sandbox '{name}' with flavor '{flavor}'...")
        result = client.create_sandbox(name, flavor)
        format_output(result, output, f"Created Sandbox: {name}")
        print_success(f"Sandbox '{name}' created successfully!")
    except Exception as e:
        print_error(f"Failed to create sandbox: {e}")
        raise typer.Exit(1)


@create_app.command("network-task")
def create_network_task(
    name: Annotated[str, typer.Argument(help="Network task name")],
    description: Annotated[str, typer.Option("--description", "-d", help="Task description")] = "Created via iq CLI",
    environment: Annotated[Optional[str], typer.Option("--environment", "-e", help="Environment name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Create a network task with a simple form."""
    # Default simple form
    form = {
        "display": "form",
        "components": [
            {
                "type": "button",
                "label": "Submit",
                "key": "submit",
                "action": "submit",
                "input": True
            }
        ]
    }

    try:
        print_info(f"Creating network task '{name}'...")
        result = client.create_network_task(name, description, form, environment=environment)
        format_output(result, output, f"Created Network Task: {name}")
        print_success(f"Network task '{name}' created successfully!")
    except Exception as e:
        print_error(f"Failed to create network task: {e}")
        raise typer.Exit(1)


# Delete commands
@delete_app.command("sandbox")
def delete_sandbox(
    sandbox_id: Annotated[str, typer.Argument(help="Sandbox ID to delete")],
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """Delete a sandbox."""
    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete sandbox '{sandbox_id}'?")
        if not confirm:
            print_warning("Operation cancelled.")
            raise typer.Exit(0)

    try:
        print_info(f"Deleting sandbox '{sandbox_id}'...")
        result = client.delete_sandbox(sandbox_id)
        print_success(f"Sandbox '{sandbox_id}' deleted successfully!")
    except Exception as e:
        print_error(f"Failed to delete sandbox: {e}")
        raise typer.Exit(1)


# Run commands
@run_app.command("job")
def run_job(
    instance_id: Annotated[str, typer.Argument(help="Instance ID")],
    name: Annotated[str, typer.Argument(help="Job name")],
    environment: Annotated[Optional[str], typer.Option("--environment", "-e", help="Environment name")] = None,
    output: Annotated[str, typer.Option("--output", "-o", help="Output format (table, json, yaml)")] = "table",
):
    """Run a job on an instance."""
    try:
        print_info(f"Running job '{name}' on instance '{instance_id}'...")
        result = client.run_job(instance_id, name, environment=environment)
        format_output(result, output, "Job Started")
        print_success(f"Job '{name}' started successfully!")
    except Exception as e:
        print_error(f"Failed to run job: {e}")
        raise typer.Exit(1)


# Config commands
@config_app.command("set-api-url")
def set_api_url(url: Annotated[str, typer.Argument(help="API URL")]):
    """Set the API URL."""
    config.api_url = url
    print_success(f"API URL set to: {url}")


@config_app.command("set-frontend-url")
def set_frontend_url(url: Annotated[str, typer.Argument(help="Frontend URL")]):
    """Set the frontend URL."""
    config.frontend_url = url
    print_success(f"Frontend URL set to: {url}")


@config_app.command("set-environment")
def set_environment(env: Annotated[str, typer.Argument(help="Default environment")]):
    """Set the default environment."""
    config.default_environment = env
    print_success(f"Default environment set to: {env}")


@config_app.command("set-output")
def set_output(format_type: Annotated[str, typer.Argument(help="Output format (table, json, yaml)")]):
    """Set the default output format."""
    if format_type not in ["table", "json", "yaml"]:
        print_error("Invalid output format. Use: table, json, or yaml")
        raise typer.Exit(1)

    config.output_format = format_type
    print_success(f"Default output format set to: {format_type}")


@config_app.command("view")
def view_config():
    """View current configuration."""
    print_info("Current configuration:")
    print(f"  API URL: {config.api_url}")
    print(f"  Frontend URL: {config.frontend_url}")
    print(f"  Default Environment: {config.default_environment}")
    print(f"  Output Format: {config.output_format}")
    print(f"  Authenticated: {auth_manager.is_authenticated()}")


@app.command()
def version():
    """Show version information."""
    from . import __version__
    print(f"iq CLI version {__version__}")


if __name__ == "__main__":
    app()
