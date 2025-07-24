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

```
cat > requirements-dev.txt << 'EOF'
```