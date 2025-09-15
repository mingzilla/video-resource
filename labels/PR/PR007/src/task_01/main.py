def main():
    from shared_utils.env_var_defaults import EnvVarDefaults
    from .py_args import PyArgs001

    envvars = EnvVarDefaults()  # Line 1: Single source of truth
    py_args = PyArgs001.create_from(envvars)  # Line 2: Config resolution


if __name__ == '__main__':
    exit(main())