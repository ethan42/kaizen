import json
import os
import sys
import git
import github

from neurosymbolic import compute
from langchain_community.tools import ReadFileTool, WriteFileTool
from langchain_community.tools import ListDirectoryTool


def main():
    """
    Run in a Git context for a GitHub project and pushes
    a PR for the most meaningful changes.

    This function checks if the current directory is a Git repository and if the remote is a GitHub project. It creates a new branch, applies changes, and pushes a pull request.

    Raises:
        SystemExit: If not in a git context or not a GitHub project.
    """

    # Check if we are in a git context
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        print("Not in a git context. Exiting.")
        sys.exit(1)

    # Get the remote GitHub URL
    remote = repo.remote().url
    print("Remote:", remote)
    print("Current contents: ", os.listdir())
    if not remote.startswith("git@github.com:") and not remote.startswith("https://github.com/"):
        print("Not a GitHub project. Exiting.")
        sys.exit(1)

    owner, project = remote.split(":")[1].split("/")[-2:]
    current_branch = repo.active_branch.name

    # Check if there exists a git configured user globally
    try:
        if not repo.config_reader().has_option("user", "name"):
            # configure it
            print("No global git user found. Configuring it.")
            repo.git.config("--global", "user.name", "kaizenbot42")
            repo.git.config("--global", "user.email", "kaizenbot42@youcanthankmelater.com")
    except Exception as exn:
        print("Error configuring git user:", exn)

    branch_name = "kaizen"

    # Create a branch named `branch_name` and erase any existing branch
    branch = repo.create_head(branch_name, force=True)
    branch.checkout()

    tools = [ListDirectoryTool(verbose=True), ReadFileTool(verbose=True), WriteFileTool(verbose=True)]
    result, _ = compute("Your current directory is a git repository. Pick a file from the repository and apply a small, yet concrete and important improvement. Edit the files directly. Focus on the code, docs, quality, not menial details like .gitignore. \n\nFinally return a title (very short) for the Pull Request describing the changes you made.", tools)

    print("Result:", result)

    result = json.loads(result)
    pr_title = result["result"]
    commit_msg = result["result"]

    # Added a check for empty commit messages
    if not commit_msg.strip():
        print("Commit message cannot be empty. Exiting.")
        sys.exit(1)

    # Add all changes
    repo.git.add(".")

    # Commit the changes for all files changed
    repo.index.commit(commit_msg)

    # Force push the changes
    repo.git.push("origin", branch, force=True)

    # Create a PR
    gh = github.Github(os.getenv("GITHUB_TOKEN"))
    gh_repo = gh.get_repo(f"{owner}/{project}")
    pull = gh_repo.create_pull(title=pr_title, head=branch_name, base=current_branch, body=commit_msg)
    print("\nPR created successfully, %s.", pull.html_url)

    # restore the original branch
    repo.git.checkout(current_branch)