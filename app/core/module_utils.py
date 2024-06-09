import importlib
import pkgutil
from types import ModuleType


def resolve_module_plugins(module: ModuleType):
    for _, module_name, _ in pkgutil.walk_packages(module.__path__):
        importlib.import_module(f"{module.__name__}.{module_name}")
        try:
            importlib.import_module(f"{module.__name__}.{module_name}.crons")
        except ModuleNotFoundError:
            pass
