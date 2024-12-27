# Kaizen: A Tool for Continuous Improvement

Kaizen is a tool that will automatically suggest improvements to your repository via PRs. Running it has two main requirements:

1. An OPENAI_API_KEY token for querying OpenAI's API and fetching suggestions.
2. A GITHUB_TOKEN with sufficient permissions to allow creating PRs in your repository.

## Configuration

Before running Kaizen, you need to configure the following environment variables:

- **OPENAI_API_KEY**: This is your API key for accessing OpenAI's services. You can obtain it from the OpenAI platform.
- **GITHUB_TOKEN**: This token must have permissions to create pull requests in your repository. You can generate a personal access token from your GitHub account settings.

Set these environment variables in your shell or CI/CD environment to ensure Kaizen can authenticate and perform its tasks.

## Running Kaizen

### Through the CLI

To run, simply run it at the top-level folder of your GitHub repository:

```sh
$ export OPENAI_API_KEY=...
$ export GITHUB_TOKEN=...
$ kaizen
```

### Through the GitHub Action

Kaizen is also available as a GitHub action, to enable it in your repo add the following in your action file:

```yaml
    - name: Kaizen for Continuous Improvement
      uses: ethan42/kaizen@main
      with:
        openai-api-key: ${{ secrets.OPENAI_API_KEY }}
        github-token: ${{ secrets.GITHUB_TOKEN }}
```

## Developing Kaizen

### Installation

Installing and running locally is as simple as:

```sh
$ poetry install
$ poetry run kaizen
```

## Contributions

We welcome contributions to Kaizen! Please ensure that your contributions adhere to the following guidelines:

1. **Code Quality**: Ensure your code is well-structured and follows the project's coding standards.
2. **Documentation**: Update the documentation to reflect any changes made.
3. **Testing**: Include tests for any new features or bug fixes.
4. **Pull Requests**: Submit your changes via pull requests, and ensure they are linked to an issue if applicable.

Thank you for helping us improve Kaizen!

## License
