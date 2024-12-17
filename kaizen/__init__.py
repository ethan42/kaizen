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

    # Create a branch named `kaizen` and erase any existing branch
    branch = repo.create_head("kaizen", force=True)
    branch.checkout()

    # Make the most meaningful changes
    # TBD
    pr_title = "[kaizen]: Improvements"
    commit_msg = "Improvements"

    # Commit the changes
    repo.index.commit("Kaizen changes")

    # Force push the changes
    repo.git.push("origin", branch, force=True)

    # Create a PR
    gh = github.GitHub()
    gh.create_pr(owner, project, pr_title, commit_msg)
    print("PR created successfully.")
