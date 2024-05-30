from app.core.utilities import BaseUtility


class HelloUtility(BaseUtility):
    name = "hello"
    description = "A simple utility that greets the user"

    def run(self, name: str) -> str:
        return f"Hello, {name}!"
