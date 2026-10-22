## Virtual Environment

### Create a virtual env

```shell
python -m venv .venv
```

### Activate virtual env

* `start.ps1`
* `start.ps`

```shell
.\my-env\Scripts\activate
```

It would then look like this `(my-env) $`

### Deactivate virtual env

```shell
.\my-env\Scripts\deactivate
```

### Install a Package

* this package will only be installed to the activated environment
* IDE - add interpreter - `docs/ide-v-env-config.png`

```shell
pip install xxx
```

or

```shell
pip install -r requirements.txt
```

### Delete a virtual envs

* after deactivating, simply just delete the venv directory

----

## Python Interpreter

* start: type `python`
* exit: type `exit()`