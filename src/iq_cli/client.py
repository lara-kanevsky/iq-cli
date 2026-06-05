"""HTTP client for iquall API."""

import requests
from typing import Any, Dict, Optional
from .config import config
from .auth import auth_manager


class IquallClient:
    """Client for interacting with iquall API."""

    def __init__(self):
        self.api_url = config.api_url
        self.frontend_url = config.frontend_url

    def _get_headers(self, user_id: str = "1", source: str = "backend", environment: Optional[str] = None) -> dict:
        """Build headers for API requests."""
        headers = {
            'Content-Type': 'application/json',
            'user_id': user_id,
            'source': source,
        }

        if environment:
            headers['environment'] = environment

        return headers

    def _make_graphql_request(self, query: str, variables: Optional[Dict] = None, environment: Optional[str] = None) -> Dict[str, Any]:
        """Make a GraphQL request to the API."""
        if not auth_manager.is_authenticated():
            raise Exception("Not authenticated. Please run 'iq login' first.")

        # Get session with cookies
        session = auth_manager.get_session()

        env = environment or config.default_environment
        headers = self._get_headers(environment=env)

        payload = {
            'query': query,
            'variables': variables or {}
        }

        print(f"Making request to {self.api_url}")
        print(f"Headers: {headers}")
        print(f"Cookies: {dict(session.cookies)}")
        print(f"Query: {query[:100]}...")

        response = session.post(
            self.api_url,
            json=payload,
            headers=headers
        )

        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")

        response.raise_for_status()
        return response.json()

    def get_sandboxes(self, first: int = 100, sandbox_name: Optional[str] = None) -> Dict[str, Any]:
        """Get list of sandboxes."""
        if sandbox_name:
            query = """
            query getSandbox($name: Filter) {
                sandboxes(first: 1, filter: { name: { eq: $name } }) {
                    edges {
                        id
                        name
                        state
                        resource_allocation {
                            id
                            flavor
                        }
                        associates {
                            username
                        }
                    }
                }
            }
            """
            variables = {"name": sandbox_name}
        else:
            query = f"""
            query getSandboxes {{
                sandboxes(first: {first}) {{
                    edges {{
                        id
                        name
                        state
                        resource_allocation {{
                            id
                            flavor
                        }}
                        associates {{
                            username
                        }}
                    }}
                }}
            }}
            """
            variables = None

        return self._make_graphql_request(query, variables)

    def create_sandbox(self, name: str, flavor: str = "FULL") -> Dict[str, Any]:
        """Create a new sandbox."""
        query = """
        mutation createSandbox($name: String!, $flavor: sandboxFlavor) {
            createSandbox(name: $name, flavor: $flavor) {
                id
                state
                resource_allocation {
                    id
                    flavor
                }
                associates {
                    username
                }
            }
        }
        """
        variables = {
            "name": name,
            "flavor": flavor
        }

        return self._make_graphql_request(query, variables)

    def delete_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """Delete a sandbox."""
        query = """
        mutation destroySandbox($sandbox_id: ID!) {
            destroySandbox(sandbox_id: $sandbox_id)
        }
        """
        variables = {"sandbox_id": sandbox_id}

        return self._make_graphql_request(query, variables)

    def get_deployment(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get deployment information."""
        query = """
        query getDeployment($environment: Environment!) {
            deployment(environment: $environment) {
                status
                branched_from
                latest_version
                info {
                    branch
                    commits_behind
                    changes {
                        total_changes
                    }
                }
            }
        }
        """
        env = environment or config.default_environment
        variables = {"environment": env}

        return self._make_graphql_request(query, variables, environment=env)

    def get_network_task(self, instance_id: str, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get network task details."""
        query = """
        query getDetailsNetworkTask($environment: Environment!, $instance_id: FilterType!) {
            applicationInstances(environment: $environment, first: 1, filter: { instance_id: { eq: $instance_id } }) {
                edges {
                    ... on NetworkTask {
                        instance_id
                        info {
                            name
                            description
                        }
                        active
                        deploy_status
                    }
                }
            }
        }
        """
        env = environment or config.default_environment
        variables = {
            "environment": env,
            "instance_id": instance_id
        }

        return self._make_graphql_request(query, variables, environment=env)

    def create_network_task(self, name: str, description: str, form: Dict, environment: Optional[str] = None) -> Dict[str, Any]:
        """Create a network task."""
        query = """
        mutation createNetworkTask($input: inputNetworkTask!) {
            instanceNetworkTask(input: $input) {
                instance_id
            }
        }
        """
        variables = {
            "input": {
                "name": name,
                "description": description,
                "form": form
            }
        }

        return self._make_graphql_request(query, variables, environment=environment)

    def update_network_task(self,
                           instance_id: str,
                           network_status: Optional[Dict] = None,
                           max_jobs_queued: Optional[int] = None,
                           concurrence: Optional[int] = None,
                           queue_policy: Optional[Dict] = None,
                           alarm_policy: Optional[Dict] = None,
                           environment: Optional[str] = None) -> Dict[str, Any]:
        """Update network task configuration."""
        query = """
        mutation updateNetworkStatusTask($instance_id: ID!, $input: inputNetworkTask!) {
            updateNetworkTask(instance_id: $instance_id, input: $input) {
                ... on NetworkTask {
                    max_jobs_queued
                    concurrence {
                        limit
                        __typename
                    }
                    network_status {
                        global_freeze_activated
                        global_freeze_deactivated
                        global_maintenance_activated
                        global_maintenance_deactivated
                        host_freeze_activated
                        host_freeze_deactivated
                        host_maintenance_activated
                        host_maintenance_deactivated
                        __typename
                    }
                    queue_policy {
                        add_on_freeze
                        add_on_maintenance
                        __typename
                    }
                    alarm_policy {
                        on_success
                        key_format
                        timeout
                        __typename
                    }
                    __typename
                }
                __typename
            }
        }
        """

        # Build input object dynamically based on provided parameters
        input_obj = {}

        if network_status:
            input_obj["network_status"] = network_status

        if max_jobs_queued is not None:
            input_obj["max_jobs_queued"] = max_jobs_queued

        if concurrence is not None:
            input_obj["concurrence"] = concurrence

        if queue_policy:
            input_obj["queue_policy"] = queue_policy

        if alarm_policy:
            input_obj["alarm_policy"] = alarm_policy

        variables = {
            "instance_id": instance_id,
            "input": input_obj
        }

        return self._make_graphql_request(query, variables, environment=environment)

    def run_job(self, instance_id: str, name: str, params: Optional[Dict] = None, environment: Optional[str] = None) -> Dict[str, Any]:
        """Run a job."""
        query = """
        mutation runJob($environment: Environment!, $instance_id: ID, $params: JSON, $name: String) {
            runJob(environment: $environment, instance_id: $instance_id, params: $params, name: $name) {
                job_id
                job_name
                status {
                    code
                    category
                    message
                }
            }
        }
        """
        env = environment or config.default_environment
        variables = {
            "environment": env,
            "instance_id": instance_id,
            "params": params or {},
            "name": name
        }

        return self._make_graphql_request(query, variables, environment=env)

    def get_job_status(self, job_id: str, environment: Optional[str] = None) -> Dict[str, Any]:
        """Get job status."""
        query = """
        query getJobDetails($job_id: FilterType, $environment: Environment!) {
            jobs(environment: $environment, filter: { job_id: { eq: $job_id } }, first: 1) {
                totalCount
                edges {
                    job_id
                    app_id
                    instance_id
                    job_name
                    execution_date
                    status {
                        code
                        message
                        category
                    }
                }
            }
        }
        """
        env = environment or config.default_environment
        variables = {
            "environment": env,
            "job_id": job_id
        }

        return self._make_graphql_request(query, variables, environment=env)

    def get_jobs_with_filter(self,
                             first: int = 10,
                             instance_id: Optional[str] = None,
                             app_id: Optional[str] = None,
                             order_by: str = "desc",
                             before: Optional[str] = None,
                             after: Optional[str] = None,
                             environment: Optional[str] = None) -> Dict[str, Any]:
        """Get jobs with filters and pagination."""
        query = """
        query getJobsWithFilter($filter: inputJobFilter, $first: Int!, $orderBy: inputJobSort, $before: ID, $after: ID, $environment: Environment!) {
            jobs(
                environment: $environment
                filter: $filter
                first: $first
                orderBy: $orderBy
                before: $before
                after: $after
            ) {
                totalCount
                pageInfo {
                    endCursor
                    hasNextPage
                    startCursor
                    hasPreviousPage
                    __typename
                }
                edges {
                    dry_run
                    instance {
                        team {
                            name
                            __typename
                        }
                        __typename
                    }
                    status {
                        stage
                        code
                        type
                        category
                        icon
                        label {
                            EN
                            ES
                            __typename
                        }
                        message
                        __typename
                    }
                    ... on NetworkTaskJob {
                        duration
                        job_id
                        app_id
                        state
                        execution_date
                        started_date
                        job_name
                        instance_id
                        final_status {
                            code
                            label
                            type
                            __typename
                        }
                        instance {
                            info {
                                name
                                __typename
                            }
                            use_case {
                                id
                                __typename
                            }
                            __typename
                        }
                        trigger {
                            ... on ManualTrigger {
                                source
                                launcher {
                                    name
                                    __typename
                                }
                                __typename
                            }
                            ... on OrchestrationTrigger {
                                source
                                job_launcher {
                                    job_id
                                    job_name
                                    instance_id
                                    app_id
                                    __typename
                                }
                                launcher {
                                    name
                                    __typename
                                }
                                __typename
                            }
                            ... on JobTrigger {
                                source
                                job_launcher {
                                    job_id
                                    job_name
                                    instance_id
                                    app_id
                                    __typename
                                }
                                launcher {
                                    name
                                    __typename
                                }
                                __typename
                            }
                            ... on HTTPEndpointTrigger {
                                source
                                endpoint_launcher
                                __typename
                            }
                            ... on UnitTestTrigger {
                                source
                                launcher {
                                    name
                                    id
                                    __typename
                                }
                                __typename
                            }
                            ... on NetworkConfigEventTrigger {
                                params
                                source
                                ncm_event_launcher {
                                    ncm_id
                                    ncm_event_id
                                    __typename
                                }
                                __typename
                            }
                            ... on ContinuousSchedule {
                                source
                                __typename
                            }
                        }
                        __typename
                    }
                }
            }
        }
        """

        env = environment or config.default_environment

        # Build filter object
        filter_obj = {}
        if instance_id:
            filter_obj["instance_id"] = {"eq": instance_id}
        if app_id:
            filter_obj["app_id"] = {"eq": app_id}

        # Build orderBy object
        order_by_obj = {"execution_date": order_by}

        variables = {
            "environment": env,
            "first": first,
            "orderBy": order_by_obj,
            "filter": filter_obj if filter_obj else None
        }

        # Add optional pagination parameters
        if before:
            variables["before"] = before
        if after:
            variables["after"] = after

        return self._make_graphql_request(query, variables, environment=env)


# Global client instance
client = IquallClient()
