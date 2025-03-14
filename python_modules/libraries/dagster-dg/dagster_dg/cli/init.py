from typing import Optional

import click

from dagster_dg.cli.scaffold import DEFAULT_WORKSPACE_NAME
from dagster_dg.cli.shared_options import dg_editable_dagster_options, dg_global_options
from dagster_dg.config import normalize_cli_config
from dagster_dg.context import DgContext
from dagster_dg.scaffold import scaffold_project, scaffold_workspace
from dagster_dg.utils import DgClickCommand, exit_with_error


@click.command(name="init", cls=DgClickCommand)
@dg_editable_dagster_options
@dg_global_options
def init_command(
    use_editable_dagster: Optional[str],
    use_editable_components_package_only: Optional[str],
    **global_options: object,
):
    """Initialize a new Dagster workspace and a first project within that workspace.

    The scaffolded workspace folder has the following structure:

    \b
    ├── dagster-workspace
    │   ├── projects
    |   |   └── <Dagster projects go here>
    |   ├── libraries
    |   |   └── <Shared packages go here>
    │   └── pyproject.toml

    """  # noqa: D301
    cli_config = normalize_cli_config(global_options, click.get_current_context())

    workspace_name = click.prompt(
        "Enter the name of your Dagster workspace",
        type=str,
        default=DEFAULT_WORKSPACE_NAME,
    ).strip()

    workspace_path = scaffold_workspace(workspace_name)
    workspace_dg_context = DgContext.from_file_discovery_and_command_line_config(
        workspace_path, cli_config
    )

    project_name = click.prompt(
        "Enter the name of your first Dagster project (or press Enter to continue without creating a project)",
        type=str,
        default="",
        show_default=False,
    ).strip()

    if not project_name:
        click.echo(
            "Continuing without adding a project. You can create one later by running `dg scaffold project`."
        )
    else:
        workspace_dg_context = DgContext.from_file_discovery_and_command_line_config(
            workspace_path, cli_config
        )
        if workspace_dg_context.has_project(project_name):
            exit_with_error(f"A project named {project_name} already exists.")

        project_path = workspace_dg_context.get_workspace_project_path(project_name)

        scaffold_project(
            project_path,
            workspace_dg_context,
            use_editable_dagster=use_editable_dagster,
            use_editable_components_package_only=use_editable_components_package_only,
            skip_venv=False,
            populate_cache=True,
        )

        click.echo("You can create additional projects later by running `dg scaffold project`.")
