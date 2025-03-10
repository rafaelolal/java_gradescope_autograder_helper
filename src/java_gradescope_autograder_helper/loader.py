import importlib.util

from .helpers import ConfigurationError


def load_module(module_path: str, module_name: str = "tests") -> object:
    """
    Load a module from the specified file path.

    Raises:
        ConfigurationError: If the module cannot be loaded from the given
            path.
    """

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ConfigurationError(
            f'Could not create module specification to load module "{module_name} from file path "{module_path}".'
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
