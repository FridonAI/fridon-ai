from app.core.plugins.utilities import BaseUtility


class HelloUtility(BaseUtility):
    def arun(self, name: str) -> str:
        return f"Hello, {name}!"
