# docuwise
my hobby project on the path of becoming a Data Architect with LLM knowledge

# Day3 Installations
* Lets first install the UV Package manager globally

```sh
pip install uv
```
* Create a virtual env with uv at the root of the repo
```sh
cd docuwise
uv venv
.\.venv\Scripts\activate
```

* Initialize the project with uv
`uv init .`
* This create main.py, pyproject.toml, .python-version and uv.lock files.
* Register your dev-tool dependencies

`uv add --dev ruff black isort mypy pre-commit`

* Install all declared dependencies
`uv sync`

* Add .venv/ folder to .gitignore file.


### ruff
* A fast, all-in-one linter that catches syntax errors, unused imports/variables, undefined names, style violations, and more. It helps you spot bugs and enforce best practices before code even runs.

### black
* An “uncompromising” code formatter that automatically rewrites your Python files to a consistent style. By outsourcing formatting decisions to Black, you avoid bike-shedding over tabs vs. spaces or line-break placement, and ensure every file looks the same.

### isort
* A tool dedicated to sorting and grouping your import statements (standard library, third-party, local). Consistent import ordering makes your code easier to scan, prevents merge conflicts in import blocks, and complements what Black does for overall formatting.

### mypy
* A static type checker for Python. By annotating your functions and variables with types and running Mypy, you catch type-mismatch errors (e.g. passing a string where a list is expected) before runtime. This dramatically reduces a whole class of bugs and makes code easier to understand and refactor.

-----------
* Together, these four form a lightweight “quality gate”:
* ruff finds things that are outright wrong or risky.
* black and isort enforce a uniform style so your team never debates formatting.
* mypy gives you confidence in your code’s correctness through static typing.
* Automating them via pre-commit hooks means every time you commit, your code is automatically linted, formatted, and type-checked—keeping your codebase clean and bug-resistant.
------------

### pre-commit hook
* A pre-commit hook is simply a script (or tool) that runs automatically on the files you’re about to commit, so it can format, lint, or reject commits that don’t meet your rules. You configure which tools to run and on which files in a single YAML file called .pre-commit-config.yaml. When you run pre-commit install, Git will call these tools for you before every commit.

# Day 4 - Setup pre-commit to automatically run your formatters, linter, and type checker on every commit.

* Create a .pre-commit-config.yaml file.

```yaml
repos:
  #1) Black - uncomppromising code formatter
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3

  #2) isort - sort and group imports
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort (python)
        language_version: python3

  #3) ruff - fast, all-in-one linter
  - repo: https://github.com/charliemarsh/ruff
    rev: 0.0.258
    hooks:
      - id: ruff

  #4) mypy - static type checker
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.1
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]

  #5 ) Cleanup hooks - remove trailing spaces & ensure newline at EOF
  - repo: https/github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer

```

* Install the hooks once
`pre-commit install`

* Run them on all files (first time)
`pre-commit run --all-files`
Test trailing space

# Day 6

```bash
mkdir -p data

uv add langchain pypdf
uv sync
```

* In your project root, create `demo.py`.

# Day 8: Embeddings

* Create an OpenAI API Key
* Install openai python package
```bash
uv add openai tiktoken
uv sync
```

# Day 9: FAISS Vector Store

```bash
pip install faiss-cpu numpy
```
