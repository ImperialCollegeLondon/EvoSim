# Installing EVOLVE

## Installation for users

The latest package can be installed with:

```bash
pip install git+https://github.com/ImperialCollegeLondon/Evolve.git@main
```

Specific versions or branches (e.g. "develop") can be installed by replacing "main" with
the name of the commit, tag, or branch.

The only pre-requisite is python 3.8 or higher and [git](https://git-scm.com/).

## Installation for Developers

### Initial setup

The pre-requisite for development are python 3.8 or higher, the python package manager
[poetry](https://python-poetry.org/), and [git](https://git-scm.com/).

EVOLVE can be installed for development with:

```bash
# Clone the repository
git clone https://github.com/ImperialCollegeLondon/Evolve
# Move to the directory with the source files
cd Evolve
# Switch to a new branch
git switch -c my_new_branch origin/develop
# Install a virtual environment with the EVOLVE package
poetry install
# Start hacking!!
```

All development should occur in a branch starting from "develop". It should be merged
back into the development branch "develop" via a pull-request.

It is recommended to use [pre-commit](https://pre-commit.com/). It will run a number of
tests before each commit to help maintain code quality. For instance, it will run
[black](https://github.com/psf/black) to ensure the code is formatted in a consistent
manner. To enable [pre-commit](https://pre-commit.com/) on your worktree, first install
it, then run:

```bash
pre-commit install
```

### Testing

EVOLVE is a develop using the [Test Driven Development
methodology](https://en.wikipedia.org/wiki/Test-driven_development). In practice, it
means many test have been written ensuring that each part of the code works as expected.

```bash
poetry run pytest
```

### Documentation

The documentation can be generated with:

```bash
poetry run sphinx-build -b html docs/source/ docs/build/
```

Then open the file "docs/build/index.html" with a browser.

### Prepering a new release

Once it is time for a new release, run the following steps:

1. create a new branch:
   
   ```bash
   git fetch origin
   git switch -c release_XXX origin/develop
   ```

1. bump the version up 

   ```bash
   poetry run bump2version minor
   ```

1. open a PR against "develop" and merge
1. open a PR from "develop" to "main" and merge
1. release [via github](https://docs.github.com/en/github/administering-a-repository/managing-releases-in-a-repository)
