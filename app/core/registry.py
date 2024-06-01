import importlib
import pkgutil
from contextvars import ContextVar
from types import ModuleType

from pydantic.v1 import BaseModel

from app.core.plugins import BasePlugin


class PluginRegistry(BaseModel):
    plugins: dict[str, type[BasePlugin]] = {}

    @property
    def plugins_list(self) -> list[type[BasePlugin]]:
        return list(self.plugins.values())

    def register(self, plugin: type[BasePlugin]):
        self.plugins[plugin.__name__] = plugin
        return plugin

var_plugin_registry = ContextVar("plugin_registry", default=PluginRegistry())


def ensure_plugin_registry() -> PluginRegistry:
    return var_plugin_registry.get()


def resolve_module_plugins(module: ModuleType):
    for _, module_name, _ in pkgutil.walk_packages(module.__path__):
        importlib.import_module(f"{module.__name__}.{module_name}")
