import importlib.util

def load_module(module_path: str, module_name: str = "tests") -> object:
    """
    Load a module from the specified file path.

    Raises:
        ConfigurationError: If the module cannot be loaded from the given
            path.
    """

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        # If this occurs, the program cannot proceed at all.
        raise Exception(
            f'Could not create module specification to load module "{module_name} from file path "{module_path}".'
        )

    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise Exception(
            f"Loader for module '{module_name}' is None. Cannot load the module from '{module_path}'."
        )

    spec.loader.exec_module(module)
    return module
