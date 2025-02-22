import importlib.util


def load_module(module_path: str, module_name: str = "tests") -> object:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise ImportError(module_path)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
