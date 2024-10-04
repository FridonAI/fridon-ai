import importlib
import pkgutil
from contextvars import ContextVar
from types import ModuleType

from pydantic import BaseModel

from fridonai_core.plugins import BasePlugin


class PluginRegistry(BaseModel):
    plugins: dict[str, type[BasePlugin]] = {}

    @property
    def plugins_list(self) -> list[type[BasePlugin]]:
        return list(self.plugins.values())

    def register(self, name: str) -> callable:
        def wrapper(plugin: type[BasePlugin]):
            self.plugins[name] = plugin
            return plugin

        return wrapper

var_plugin_registry = ContextVar("plugin_registry", default=PluginRegistry())


def ensure_plugin_registry() -> PluginRegistry:
    return var_plugin_registry.get()


def resolve_module_plugins(module: ModuleType):
    for _, module_name, _ in pkgutil.walk_packages(module.__path__):
        importlib.import_module(f"{module.__name__}.{module_name}")
