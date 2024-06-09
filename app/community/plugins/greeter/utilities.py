from app.core.plugins.utilities import BaseUtility


class HelloUtility(BaseUtility):
    def arun(self, name: str | None = None, *args, **kwargs) -> str:
        return f"Hello, {name}!"
