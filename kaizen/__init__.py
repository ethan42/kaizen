import sys
import git
import github



def main():
    """
    Run in a Git context for a GitHub project and pushes
    a PR for the most meaningful changes.
    """

    # Check if we are in a git context
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        print("Not in a git context. Exiting.")
        sys.exit(1)

    # Get the remote GitHub URL
    remote = repo.remote().url
    if not remote.startswith("git@github.com:"):
        print("Not a GitHub project. Exiting.")
        sys.exit(1)

    owner, project = remote.split(":")[1].split("/")[-2:]

    branch_name = "kaizen"

    current_branch = repo.active_branch.name

    # Create a branch named `branch_name` and erase any existing branch
    branch = repo.create_head(branch_name, force=True)
    branch.checkout()

    # Make the most meaningful changes
    # TBD
    pr_title = "Improvements"
    commit_msg = "Improvements"

    # Commit the changes
    repo.index.commit(commit_msg)

    # Force push the changes
    repo.git.push("origin", branch, force=True)

    # Create a PR
    gh = github.Github(os.getenv("GITHUB_TOKEN"))
    gh_repo = gh.get_repo(f"{owner}/{project}")
    gh_repo.create_pull(title=pr_title, head=branch_name, base=current_branch, body=commit_msg)
    print("PR created successfully.")

    # restore the original branch
    repo.git.checkout(current_branch)
