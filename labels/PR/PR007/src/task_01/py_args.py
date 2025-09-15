from shared_utils.env_var_defaults import EnvVarDefaults

class PyArgs001:
    def __init__(self, envvars: EnvVarDefaults):
        # CRITICAL: NO argparse, NO CLI args - envvars only
        self.embedding_model: str = envvars.embedding_model

    @classmethod
    def create_from(cls, envvars: EnvVarDefaults) -> 'PyArgs001':
        # Direct envvar usage - NO CLI parsing ever
        return cls(envvars)
