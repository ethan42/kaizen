import json
import os
import sys
import git
import github

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import GitLoader

from neurosymbolic import compute
from langchain_community.tools import ReadFileTool, WriteFileTool


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
    current_branch = repo.active_branch.name

    # Decide what the most meaningful changes are
    git_doc_repo = GitLoader(
        repo_path=".",
        branch=current_branch
    ).load()

    prompt = ChatPromptTemplate.from_messages(
        [("system", "Suggest a small, yet concrete improvement that should be performed in the following repository. Focus on the code, docs, quality, not menial details like .gitignore. Provide the list of file paths of files that need to be changed (use the git repository metadata you are given to figure out file paths, don't guess) and a brief description of the suggested changes. Here is the repo:\\n\\n{context}")]
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = create_stuff_documents_chain(llm, prompt)
    improvements = chain.invoke({"context": git_doc_repo})

    print("Improvements:", improvements)

    branch_name = "kaizen"

    # Create a branch named `branch_name` and erase any existing branch
    branch = repo.create_head(branch_name, force=True)
    branch.checkout()

    tools = [ReadFileTool(verbose=True), WriteFileTool(verbose=True)]
    result, _ = compute("I need you to perform modifications on the local git repository." + improvements + "\n\nReturn a title (very short) for the Pull Request describing the changes.", tools)

    print("Result:", result)

    result = json.loads(result)
    pr_title = result["result"]
    commit_msg = result["result"]

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
