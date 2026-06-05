# iq CLI - iquall Command Line Interface

A kubectl-style CLI tool for interacting with the iquall system.

## Installation

```bash
cd iq-cli
uv pip install -e .
```

Or if using pip:

```bash
cd iq-cli
pip install -e .
```

## Quick Start

### 1. Authentication

First, authenticate with the iquall system:

```bash
iq login --email your@email.com --password yourpassword
```

Or use interactive mode:

```bash
iq login
```

### 2. Configuration

Configure your API endpoints (optional, defaults are already set):

```bash
# Set API URL
iq config set-api-url http://core-api.mat.svc.cluster.local:8000

# Set frontend URL
iq config set-frontend-url http://frontend.mat.svc.cluster.local:80

# Set default environment
iq config set-environment sandbox

# View current configuration
iq config view
```

### 3. Basic Usage

List sandboxes:

```bash
iq get sandboxes
```

Get deployment information:

```bash
iq get deployment
```

## Commands

### Authentication

```bash
# Login
iq login --email user@example.com --password password

# Logout
iq logout
```

### Get Resources

```bash
# Get all sandboxes
iq get sandboxes

# Get specific sandbox by name
iq get sandboxes --name "My Sandbox"

# Get deployment info
iq get deployment

# Get deployment for specific environment
iq get deployment --environment production

# Get network task details
iq get network-task <instance-id>

# Get job status
iq get job <job-id>
```

### Create Resources

```bash
# Create a sandbox
iq create sandbox "My New Sandbox"

# Create sandbox with specific flavor
iq create sandbox "My Test Sandbox" --flavor FULL

# Create a network task
iq create network-task "My Network Task" --description "Task description"
```

### Delete Resources

```bash
# Delete a sandbox (with confirmation)
iq delete sandbox <sandbox-id>

# Delete without confirmation
iq delete sandbox <sandbox-id> --yes
```

### Run Jobs

```bash
# Run a job
iq run job <instance-id> "Job Name"

# Run job in specific environment
iq run job <instance-id> "Job Name" --environment production
```

### Configuration

```bash
# Set API URL
iq config set-api-url <url>

# Set frontend URL
iq config set-frontend-url <url>

# Set default environment
iq config set-environment <environment>

# Set default output format (table, json, yaml)
iq config set-output json

# View current configuration
iq config view
```

## Output Formats

All `get` commands support multiple output formats:

```bash
# Table format (default, pretty-printed)
iq get sandboxes

# JSON format
iq get sandboxes --output json
iq get sandboxes -o json

# YAML format
iq get sandboxes --output yaml
iq get sandboxes -o yaml
```

## Environment Variables

You can also configure the CLI using environment variables:

```bash
export IQ_API_URL="http://core-api.mat.svc.cluster.local:8000"
export IQ_FRONTEND_URL="http://frontend.mat.svc.cluster.local:80"
```

## Examples

### Create and manage a sandbox

```bash
# Create a new sandbox
iq create sandbox "My Test Sandbox" --flavor FULL

# List all sandboxes to find the ID
iq get sandboxes

# Get specific sandbox details
iq get sandboxes --name "My Test Sandbox"

# Delete the sandbox when done
iq delete sandbox <sandbox-id>
```

### Check deployment status

```bash
# Get deployment info for default environment
iq get deployment

# Get deployment info for production
iq get deployment --environment production

# Get JSON output for scripting
iq get deployment --output json
```

### Run a job and check its status

```bash
# Run a job
iq run job 7mw-ddo-sml "Test Job" --environment sandbox

# Check job status
iq get job 214-zva-439 --environment sandbox
```

### Work with network tasks

```bash
# Create a network task
iq create network-task "Integration Test NT" --description "Test task"

# Get network task details
iq get network-task oc2-dxc-t1l
```

## Configuration Files

The CLI stores its configuration in `~/.iq/`:

- `~/.iq/config.yaml` - Configuration settings
- `~/.iq/cookies.txt` - Authentication cookies

## Troubleshooting

### Not authenticated error

If you see "Not authenticated" errors, run:

```bash
iq login
```

### Connection errors

Check your API URLs are correct:

```bash
iq config view
```

Update if needed:

```bash
iq config set-api-url <correct-url>
iq config set-frontend-url <correct-url>
```

## Help

Get help for any command:

```bash
# General help
iq --help

# Help for specific commands
iq get --help
iq create --help
iq delete --help
iq run --help
iq config --help

# Help for subcommands
iq get sandboxes --help
iq create sandbox --help
```

## Version

```bash
iq version
```

## Development

### Project Structure

```
iq-cli/
├── src/
│   └── iq_cli/
│       ├── __init__.py      # Package info
│       ├── main.py          # CLI commands and entry point
│       ├── client.py        # API client for iquall
│       ├── auth.py          # Authentication management
│       ├── config.py        # Configuration management
│       └── formatters.py    # Output formatting
├── pyproject.toml           # Project dependencies
└── README.md               # This file
```

### Installing in development mode

```bash
cd iq-cli
uv pip install -e .
```

## License

Internal tool for iquall system.
