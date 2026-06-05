"""Output formatters for iq CLI."""

import json
import yaml
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table


console = Console()


def format_output(data: Any, format_type: str = "table", title: str = ""):
    """
    Format and print output data.

    Args:
        data: Data to format
        format_type: Output format (table, json, yaml)
        title: Title for table output
    """
    if format_type == "json":
        print(json.dumps(data, indent=2))
    elif format_type == "yaml":
        print(yaml.dump(data, default_flow_style=False))
    elif format_type == "table":
        _format_table(data, title)
    else:
        print(data)


def _format_table(data: Any, title: str = ""):
    """Format data as a rich table."""
    if isinstance(data, dict):
        # Handle GraphQL response format
        if 'data' in data:
            _format_graphql_data(data['data'], title)
        else:
            _format_dict_table(data, title)
    elif isinstance(data, list):
        _format_list_table(data, title)
    else:
        console.print(data)


def _format_graphql_data(data: Dict, title: str):
    """Format GraphQL response data."""
    # Find the main data key
    if not data:
        console.print("[yellow]No data returned[/yellow]")
        return

    main_key = list(data.keys())[0]
    main_data = data[main_key]

    # Handle different response structures
    if isinstance(main_data, dict) and 'edges' in main_data:
        # Connection type with edges
        edges = main_data['edges']
        if edges:
            _format_list_table(edges, title or main_key.capitalize())
        else:
            console.print(f"[yellow]No {main_key} found[/yellow]")
    elif isinstance(main_data, list):
        if main_data:
            _format_list_table(main_data, title or main_key.capitalize())
        else:
            console.print(f"[yellow]No {main_key} found[/yellow]")
    elif isinstance(main_data, dict):
        _format_dict_table(main_data, title or main_key.capitalize())
    else:
        console.print(main_data)


def _format_dict_table(data: Dict, title: str):
    """Format a dictionary as a two-column table."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        table.add_row(key, value_str)

    console.print(table)


def _format_list_table(data: List[Dict], title: str):
    """Format a list of dictionaries as a table."""
    if not data:
        console.print("[yellow]No data to display[/yellow]")
        return

    # Get all unique keys from all items
    all_keys = set()
    for item in data:
        all_keys.update(_flatten_dict(item).keys())

    # Create table
    table = Table(title=title, show_header=True, header_style="bold magenta")

    # Add columns
    for key in sorted(all_keys):
        table.add_column(key.replace('_', ' ').title(), style="cyan")

    # Add rows
    for item in data:
        flat_item = _flatten_dict(item)
        row = []
        for key in sorted(all_keys):
            value = flat_item.get(key, "")
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value) if value is not None else ""
            row.append(value_str)
        table.add_row(*row)

    console.print(table)


def _flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten nested dictionary.

    Args:
        d: Dictionary to flatten
        parent_key: Prefix for keys
        sep: Separator for nested keys

    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict) and v:
            # Only flatten if it's a simple dict, otherwise keep as is
            if all(not isinstance(val, (dict, list)) for val in v.values()):
                items.extend(_flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # For lists of dicts, convert to summary
            items.append((new_key, f"[{len(v)} items]"))
        else:
            items.append((new_key, v))

    return dict(items)


def print_success(message: str):
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message."""
    console.print(f"[red]✗[/red] {message}", style="red")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")


def print_info(message: str):
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}", style="blue")
