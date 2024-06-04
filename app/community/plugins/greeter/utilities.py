from app.core.plugins.utilities import BaseUtility


class HelloUtility(BaseUtility):
    name = "hello"
    description = "A simple utility that greets the user"

    def arun(self, name: str) -> str:
        return f"Hello, {name}!"
