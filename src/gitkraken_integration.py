#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitKraken CLI Integration Module for Qwen Code
This module provides integration with the GitKraken CLI using the OpenAPI specification.
It allows Qwen to interact with GitKraken's features including AI capabilities,
workspace management, git operations, and more.
"""

import subprocess
import os
from typing import Optional, Dict, Any, List


class GitKrakenCLI:
    """A wrapper class to interact with the GitKraken CLI (`gk`).

    This class provides Python methods that map directly to the `gk`
    command-line tool's subcommands. It handles finding the `gk` executable,
    running commands, and returning the output in a structured dictionary.

    Attributes:
        cli_path (Optional[str]): The discovered path to the `gk` executable,
            or None if it could not be found.
    """

    def __init__(self):
        """Initializes the GitKrakenCLI class by finding the `gk` executable."""
        self.cli_path = self._find_gk_cli()

    def _find_gk_cli(self) -> Optional[str]:
        """Finds the GitKraken CLI executable in the system.

        It first checks the system's PATH using `which`, then looks in
        common installation directories.

        Returns:
            The absolute path to the `gk` executable as a string,
            or None if it cannot be found.
        """
        try:
            # Try to locate gk command
            result = subprocess.run(["which", "gk"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()

            # If not found in PATH, try common installation locations
            possible_paths = [
                "/usr/local/bin/gk",
                "/opt/homebrew/bin/gk",  # macOS with homebrew
                os.path.expanduser("~/bin/gk"),
                os.path.expanduser("~/.local/bin/gk"),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    return path
        except Exception:
            pass

        return None

    def is_installed(self) -> bool:
        """Checks if the GitKraken CLI is installed and found.

        Returns:
            True if the `gk` executable path is known, False otherwise.
        """
        return self.cli_path is not None

    def run_command(self, args: List[str]) -> Dict[str, Any]:
        """Runs a GitKraken CLI command and captures its output.

        This is the primary method for executing all `gk` commands. It
        constructs the full command, runs it as a subprocess, and returns
        a dictionary with the execution details.

        Args:
            args: A list of strings representing the command and its arguments
                (e.g., ['ai', 'commit', '--add-description']).

        Returns:
            A dictionary containing the command's result, including:
            - 'success' (bool): True if the command exited with code 0.
            - 'returncode' (int): The command's exit code.
            - 'stdout' (str): The standard output.
            - 'stderr' (str): The standard error.
            - 'command' (str): The full command that was executed.
            In case of an error, it returns a dictionary with 'success': False
            and an 'error' message.
        """
        if not self.is_installed():
            return {
                "success": False,
                "error": "GitKraken CLI (gk) is not installed or not in PATH",
                "output": "",
            }

        try:
            cmd = [self.cli_path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "output": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    # AI-related commands
    def ai_changelog(
        self,
        base: Optional[str] = None,
        head: Optional[str] = None,
        path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates a changelog between two commits or branches using AI.

        Args:
            base: The base branch or commit for the changelog.
            head: The head branch or commit for the changelog.
            path: The path to the repository.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["ai", "changelog"]
        if base:
            args.extend(["--base", base])
        if head:
            args.extend(["--head", head])
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    def ai_commit(
        self, add_description: bool = False, path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a new commit message with AI.

        Args:
            add_description: If True, includes a generated description in the
                commit message.
            path: The path to the repository.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["ai", "commit"]
        if add_description:
            args.append("--add-description")
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    def ai_explain_branch(
        self, branch: Optional[str] = None, path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uses AI to explain the changes in a branch.

        Args:
            branch: The branch to explain. Defaults to the current HEAD.
            path: The path to the repository.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["ai", "explain", "branch"]
        if branch:
            args.extend(["--branch", branch])
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    def ai_explain_commit(
        self, commit_sha: str, path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uses AI to explain the changes in a specific commit.

        Args:
            commit_sha: The SHA of the commit to explain.
            path: The path to the repository.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["ai", "explain", "commit", commit_sha]
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    def ai_pr_create(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Generates a new pull request with AI.

        Args:
            path: The path to the repository.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["ai", "pr", "create"]
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    def ai_resolve(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Uses AI to resolve git conflicts.

        Args:
            path: The path to the repository with conflicts.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["ai", "resolve"]
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    def ai_tokens(self) -> Dict[str, Any]:
        """Outputs the number of GitKraken AI tokens used.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["ai", "tokens"])

    # Auth-related commands
    def auth_login(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Logs into a GitKraken account.

        Args:
            token: An optional authentication token to use for login.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["auth", "login"]
        if token:
            args.extend(["--token", token])

        return self.run_command(args)

    def auth_logout(self) -> Dict[str, Any]:
        """Logs out from the current GitKraken account.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["auth", "logout"])

    # Graph-related commands
    def graph(
        self,
        gitkraken: bool = False,
        gitlens: bool = False,
        gitlens_codium: bool = False,
        gitlens_insiders: bool = False,
        path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Displays the commit graph for the current repository.

        Args:
            gitkraken: Open the graph in GitKraken Client.
            gitlens: Open the graph in GitLens in VS Code.
            gitlens_codium: Open the graph in GitLens in VSCodium.
            gitlens_insiders: Open the graph in GitLens in VS Code Insiders.
            path: The path to the repository.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["graph"]
        if gitkraken:
            args.append("--gitkraken")
        if gitlens:
            args.append("--gitlens")
        if gitlens_codium:
            args.append("--gitlens-codium")
        if gitlens_insiders:
            args.append("--gitlens-insiders")
        if path:
            args.extend(["--path", path])

        return self.run_command(args)

    # Issue-related commands
    def issue_assign(
        self,
        provider: str,
        issue_id: str,
        organization_name: str,
        repo_name: str,
        email: Optional[str] = None,
        nickname: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assigns an issue to a user.

        Args:
            provider: The issue tracking provider (e.g., 'github').
            issue_id: The ID of the issue to assign.
            organization_name: The name of the organization or user account.
            repo_name: The name of the repository.
            email: The email of the user to assign the issue to.
            nickname: The nickname of the user to assign the issue to.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = [
            "issue",
            "assign",
            provider,
            "--issue-id",
            issue_id,
            "--organization-name",
            organization_name,
            "--repo-name",
            repo_name,
        ]
        if email:
            args.extend(["--email", email])
        if nickname:
            args.extend(["--nickname", nickname])

        return self.run_command(args)

    def issue_list(self, provider: str) -> Dict[str, Any]:
        """Shows a list of issues from the specified provider.

        Args:
            provider: The issue tracking provider (e.g., 'github').

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["issue", "list", provider])

    # MCP-related commands
    def mcp_start(self, readonly: bool = False) -> Dict[str, Any]:
        """Starts a local MCP (Model Context Protocol) server.

        Args:
            readonly: If True, starts the server in read-only mode.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["mcp"]
        if readonly:
            args.append("--readonly")

        return self.run_command(args)

    def mcp_install(
        self, platform: str, file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Installs the GitKraken MCP server in an MCP client.

        Args:
            platform: The target platform for installation.
            file_path: The path to the client's configuration file.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["mcp", "install", platform]
        if file_path:
            args.extend(["--file-path", file_path])

        return self.run_command(args)

    def mcp_uninstall(
        self, platform: str, file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uninstalls the GitKraken MCP server.

        Args:
            platform: The target platform for uninstallation.
            file_path: The path to the client's configuration file.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["mcp", "uninstall", platform]
        if file_path:
            args.extend(["--file-path", file_path])

        return self.run_command(args)

    # Organization-related commands
    def organization_list(self) -> Dict[str, Any]:
        """Lists all GitKraken organizations the user is a member of.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["organization", "list"])

    def organization_set(self, name: str) -> Dict[str, Any]:
        """Sets the default GitKraken organization.

        Args:
            name: The name of the organization to set as default.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["organization", "set", name])

    def organization_unset(self) -> Dict[str, Any]:
        """Clears the default GitKraken organization setting.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["organization", "unset"])

    # Provider-related commands
    def provider_add(self, provider: str, token: str) -> Dict[str, Any]:
        """Adds an authentication token for a provider.

        Args:
            provider: The provider to add (e.g., 'github').
            token: The authentication token.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["provider", "add", provider, "--token", token])

    def provider_list(self) -> Dict[str, Any]:
        """Lists all configured provider tokens.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["provider", "list"])

    def provider_remove(self, provider: str) -> Dict[str, Any]:
        """Removes an authentication token for a provider.

        Args:
            provider: The provider to remove.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["provider", "remove", provider])

    # Version command
    def version(self) -> Dict[str, Any]:
        """Prints the version number of the GitKraken CLI.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["version"])

    # Work-related commands
    def work_list(self) -> Dict[str, Any]:
        """Lists all work items.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["work", "list"])

    def work_info(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Views information about a specific work item.

        Args:
            name: The name of the work item.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "info"]
        if name:
            args.extend(["--name", name])

        return self.run_command(args)

    def work_start(
        self,
        name: str,
        issue: Optional[str] = None,
        branch: Optional[str] = None,
        base_branch: Optional[str] = None,
        include_repos: Optional[str] = None,
        exclude_repos: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Starts a new work item.

        Args:
            name: The name for the new work item.
            issue: An issue key to link to the work item.
            branch: The name of the branch to create.
            base_branch: The base branch for the new branch.
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "start", name]
        if issue:
            args.extend(["--issue", issue])
        if branch:
            args.extend(["--branch", branch])
        if base_branch:
            args.extend(["--base-branch", base_branch])
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def work_set(self, name: str) -> Dict[str, Any]:
        """Sets the active work item.

        Args:
            name: The name of the work item to set as active.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["work", "set", name])

    def work_branch(
        self,
        base_branch: Optional[str] = None,
        include_repos: Optional[str] = None,
        exclude_repos: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new branch for the current work item.

        Args:
            base_branch: The base branch for the new branch.
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "branch"]
        if base_branch:
            args.extend(["--base-branch", base_branch])
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def work_commit(
        self,
        add_description: bool = False,
        ai: bool = False,
        include_repos: Optional[str] = None,
        exclude_repos: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Commits changes for the current work item.

        Args:
            add_description: If True, adds a generated description.
            ai: If True, uses AI to generate the commit message.
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "commit"]
        if add_description:
            args.append("--add-description")
        if ai:
            args.append("--ai")
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def work_push(
        self,
        force: bool = False,
        create_pr: bool = False,
        include_repos: Optional[str] = None,
        exclude_repos: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pushes repository changes for the current work item.

        Args:
            force: If True, performs a force push.
            create_pr: If True, creates a pull request after pushing.
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "push"]
        if force:
            args.append("--force")
        if create_pr:
            args.append("--create-pr")
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def work_pr_create(
        self,
        title: Optional[str] = None,
        body: Optional[str] = None,
        ai: bool = False,
        push: bool = False,
        include_repos: Optional[str] = None,
        exclude_repos: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new pull request for the current work item.

        Args:
            title: The title of the pull request.
            body: The body of the pull request.
            ai: If True, uses AI to generate the title and body.
            push: If True, pushes changes before creating the PR.
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "pr", "create"]
        if title:
            args.extend(["--title", title])
        if body:
            args.extend(["--body", body])
        if ai:
            args.append("--ai")
        if push:
            args.append("--push")
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def work_pr_merge(
        self, include_repos: Optional[str] = None, exclude_repos: Optional[str] = None
    ) -> Dict[str, Any]:
        """Merges existing pull requests for the current work item.

        Args:
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "pr", "merge"]
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def work_delete(self, name: str, force: bool = False) -> Dict[str, Any]:
        """Deletes a work item.

        Args:
            name: The name of the work item to delete.
            force: If True, forces the deletion.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["work", "delete", name]
        if force:
            args.append("--force")

        return self.run_command(args)

    def work_update(self) -> Dict[str, Any]:
        """Updates a work item.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["work", "update"])

    # Workspace-related commands
    def workspace_list(self) -> Dict[str, Any]:
        """Lists all workspaces.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["workspace", "list"])

    def workspace_info(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Views information about a workspace.

        Args:
            name: The name of the workspace.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["workspace", "info"]
        if name:
            args.extend(["--name", name])

        return self.run_command(args)

    def workspace_create(
        self,
        name: Optional[str] = None,
        cloud: bool = False,
        description: Optional[str] = None,
        add_repos: Optional[str] = None,
        add_members: Optional[str] = None,
        add_teams: Optional[str] = None,
        organization_name: Optional[str] = None,
        root_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Creates a new workspace.

        Args:
            name: The name of the new workspace.
            cloud: If True, creates a cloud workspace.
            description: A description for the workspace.
            add_repos: Comma-separated list of repos to add.
            add_members: Comma-separated list of members to add.
            add_teams: Comma-separated list of teams to add.
            organization_name: The name of the organization for the workspace.
            root_path: The root path for the workspace.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["workspace", "create"]
        if name:
            args.extend(["--name", name])
        if cloud:
            args.append("--cloud")
        if description:
            args.extend(["--description", description])
        if add_repos:
            args.extend(["--add-repos", add_repos])
        if add_members:
            args.extend(["--add-members", add_members])
        if add_teams:
            args.extend(["--add-teams", add_teams])
        if organization_name:
            args.extend(["--organization-name", organization_name])
        if root_path:
            args.extend(["--root-path", root_path])

        return self.run_command(args)

    def workspace_set(self, name: str) -> Dict[str, Any]:
        """Sets the default workspace.

        Args:
            name: The name of the workspace to set as default.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["workspace", "set", name])

    def workspace_unset(self) -> Dict[str, Any]:
        """Clears the active workspace setting.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["workspace", "unset"])

    def workspace_update(
        self,
        name: str,
        new_name: Optional[str] = None,
        description: Optional[str] = None,
        cloud: Optional[bool] = None,
        add_repos: Optional[str] = None,
        remove_repos: Optional[str] = None,
        add_members: Optional[str] = None,
        remove_members: Optional[str] = None,
        add_teams: Optional[str] = None,
        remove_teams: Optional[str] = None,
        azure_org: Optional[str] = None,
        azure_project: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates an existing workspace.

        Args:
            name: The current name of the workspace to update.
            new_name: A new name for the workspace.
            description: A new description for the workspace.
            cloud: Set to True to make it a cloud workspace, False for local.
            add_repos: Comma-separated list of repos to add.
            remove_repos: Comma-separated list of repos to remove.
            add_members: Comma-separated list of members to add.
            remove_members: Comma-separated list of members to remove.
            add_teams: Comma-separated list of teams to add.
            remove_teams: Comma-separated list of teams to remove.
            azure_org: The Azure organization to associate.
            azure_project: The Azure project to associate.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["workspace", "update", name]
        if new_name:
            args.extend(["--name", new_name])
        if description:
            args.extend(["--description", description])
        if cloud is not None:
            if cloud:
                args.append("--cloud")
            else:
                args.append("--no-cloud")
        if add_repos:
            args.extend(["--add-repos", add_repos])
        if remove_repos:
            args.extend(["--remove-repos", remove_repos])
        if add_members:
            args.extend(["--add-members", add_members])
        if remove_members:
            args.extend(["--remove-members", remove_members])
        if add_teams:
            args.extend(["--add-teams", add_teams])
        if remove_teams:
            args.extend(["--remove-teams", remove_teams])
        if azure_org:
            args.extend(["--azure-org", azure_org])
        if azure_project:
            args.extend(["--azure-project", azure_project])

        return self.run_command(args)

    def workspace_delete(self, name: str, force: bool = False) -> Dict[str, Any]:
        """Deletes a workspace.

        Args:
            name: The name of the workspace to delete.
            force: If True, forces the deletion without confirmation.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["workspace", "delete", name]
        if force:
            args.append("--force")

        return self.run_command(args)

    def workspace_refresh(
        self,
        name: Optional[str] = None,
        fetch_only: bool = False,
        include_repos: Optional[str] = None,
        exclude_repos: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synchronizes the state of a workspace.

        Args:
            name: The name of the workspace to refresh.
            fetch_only: If True, only fetches remote changes without pulling.
            include_repos: Comma-separated list of repos to include.
            exclude_repos: Comma-separated list of repos to exclude.

        Returns:
            A dictionary containing the result of the command execution.
        """
        args = ["workspace", "refresh"]
        if name:
            args.extend(["--name", name])
        if fetch_only:
            args.append("--fetch-only")
        if include_repos:
            args.extend(["--include-repos", include_repos])
        if exclude_repos:
            args.extend(["--exclude-repos", exclude_repos])

        return self.run_command(args)

    def workspace_clone(self, name: str, root_path: str) -> Dict[str, Any]:
        """Clones a workspace to a local directory.

        Args:
            name: The name of the workspace to clone.
            root_path: The local path where the workspace should be cloned.

        Returns:
            A dictionary containing the result of the command execution.
        """
        return self.run_command(["workspace", "clone", name, root_path])


# Example usage
if __name__ == "__main__":
    gk = GitKrakenCLI()

    if gk.is_installed():
        print("GitKraken CLI is installed!")
        result = gk.version()
        print(f"Version: {result}")
    else:
        print("GitKraken CLI is not installed or not in PATH")
