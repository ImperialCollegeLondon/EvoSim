# EvoSim

Simulation package for the [EVOLVE](https://www.imperial.ac.uk/evolve-project) project:
Electric Vehicle fleet Optimisation for lowering vehicle Emissions.

![Build Status](https://github.com/ImperialCollegeLondon/EvoSim/workflows/ci/badge.svg)

# Installation for users

The latest package can be installed with:

```bash
pip install git+https://github.com/ImperialCollegeLondon/EvoSim.git@main
```

Specific versions or branches (e.g. "develop") can be installed by replacing "main" with
the name of the commit, tag, or branch.

The only pre-requisite is python 3.8 or higher and [git](https://git-scm.com/).

# Installation for Developers

## Initial setup

The pre-requisite for development are python 3.8 or higher, the python package manager
[poetry](https://python-poetry.org/), and [git](https://git-scm.com/).

EvoSim can be installed for development with:

```bash
# Clone the repository
git clone https://github.com/ImperialCollegeLondon/EvoSim
# Move to the directory with the source files
cd EvoSim
# Switch to a new branch
git switch -c my_new_branch origin/develop
# Install a virtual environment with the EvoSim package
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

## Testing

EvoSim is developed using the [Test Driven Development
methodology](https://en.wikipedia.org/wiki/Test-driven_development). In practice, it
means many test have been written ensuring that each part of the code works as expected.
There are two types of tests:

- unittest: in the "tests/" subdirectory. They check the internal implementation of
    EvoSim.

    ```bash
    poetry run pytest
    ```

- doctest: in the "\*.rst" files with the source code. These tests are part of the
    documentation and document how EvoSim can be used and enhanced by developers.

    ```bash
    poetry run sphinx-build -E -b doctest docs build
    ```

Linux, MacOS, and Window Linux Subsystem users can run both types of tests with:

```bash
make tests
```


## Documentation

The documentation can be generated with:

```bash
poetry run sphinx-build -b html docs build
```

Then open the file "build/index.html" with a browser.

## Preparing a new release

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
