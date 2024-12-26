import json
import os
import sys
import random
import git
import github

from subprocess import run
from neurosymbolic import compute
from langchain_community.tools import ReadFileTool, WriteFileTool
from langchain_community.tools import ListDirectoryTool
from typing import NoReturn


def main() -> NoReturn:
    """
    Run in a Git context for a GitHub project and pushes
    a PR for the most meaningful changes.

    This function checks if the current directory is a Git repository and if the remote is a GitHub project. It creates a new branch, applies changes, and pushes a pull request.

    Raises:
        SystemExit: If not in a git context or not a GitHub project.
    """

    # Check if we are in a git context
    try:
        repo = git.Repo(search_parent_directories=False)
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
    if not repo.config_reader().has_option("user", "name"):
        # configure it
        print("No global git user found. Configuring it.")
        repo.git.config("--global", "user.name", "kaizenbot42")
        repo.git.config("--global", "user.email", "kaizenbot42@youcanthankmelater.com")
        # set the current directory as safe by running git config --global --add safe.directory /github/workspace
        run(["git", "config", "--global", "--add", "safe.directory", os.getcwd()])

    branch_name = "kaizen"

    # Create a branch named `branch_name` and erase any existing branch
    branch = repo.create_head(branch_name, force=True)
    branch.checkout()

    # Fetch all files in this git repository
    all_files = []
    for f in repo.head.commit.tree.traverse():
        all_files.append(f.path)

    # Choose 5 random files
    sample = ', '.join('`%s`' % filename for filename in random.sample(all_files, 5))

    tools = [ReadFileTool(verbose=True), WriteFileTool(verbose=True)]
    prompt = os.getenv("KAIZEN_PROMPT", "Your current directory is a git repository. One of the %s files have to be improved. Pick one of them and apply a concrete and impactful improvement. Edit the file directly. Focus on the code, docs, quality, not menial changes. \n\nFinally return a title (very short) for the Pull Request describing the changes you made." % sample)
    print("Prompt:", prompt)
    result, _ = compute(prompt, tools)

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
