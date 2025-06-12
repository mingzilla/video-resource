# Step-by-Step Guide to Adding Python Linting to PyCharm

* pylint flake8 black -- lint
* mypy -- typing

## Install Linting Tools:

The most commonly used Python linters are pylint, flake8, and black. You can install these tools using pip.

```sh
pip install pylint flake8 black
```

### Configure PyCharm to Use Linters:

* Open PyCharm and go to File > Settings (or PyCharm > Preferences on macOS).
* Navigate to Languages & Frameworks > Python Quality Tools > Pylint.
* Check the Enable Pylint checkbox.
* Ensure the path to the pylint executable is correct (usually, it’s in your virtual environment’s Scripts or bin directory).

### Configure Flake8:

* Navigate to Languages & Frameworks > Python Quality Tools > Flake8.
* Check the Enable Flake8 checkbox.
* Ensure the path to the flake8 executable is correct.

### Configure Black (Optional):

* Black is an opinionated code formatter, and while it’s not a linter per se, it ensures that your code adheres to a consistent style.
* Navigate to Tools > Black Formatter.
* Check the Enable Black Formatter checkbox.
* Ensure the path to the black executable is correct.
* You can also configure Black to run on save by checking the Reformat file on save option.

## Typing

```sh
pip install mypy
```

* install mypy plugins