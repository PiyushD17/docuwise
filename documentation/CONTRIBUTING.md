# DocuWise Contributing Guide

Welcome, and thanks for contributing to **DocuWise**! This guide will help you set up your development environment and get started.

## Prerequisites

- **Git**: https://git-scm.com/
- **Python 3.11+**: https://www.python.org/downloads/
- **uv** (Python package manager):

```bash
python3 -m pip install --user uv
```

## Setup

```bash
# clone repo
git clone https://github.com/your-username/docuwise.git
cd docuwise

# create venv
uv venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

# Install all dependencies
uv sync

# Install Git hooks
pre-commit install
```

* Adding new dependencies

```bash
uv add <package-name>
uv sync
```

* Adding new dev tools
```bash
uv add --dev <tool-name>
uv sync
```

| Task                             | Command                           |
| -------------------------------- | --------------------------------- |
| Sync all dependencies            | `uv sync`                         |
| Install a new runtime dependency | `uv add <pkg>` → `uv sync`        |
| Install a new dev-tool           | `uv add --dev <tool>` → `uv sync` |
| Auto-fix issues with ruff        | `ruff --fix .`                    |
| Run linter only                  | `ruff .`                          |
| Run type checks                  | `mypy src/`                       |
| Run all pre-commit hooks         | `pre-commit run --all-files`      |
