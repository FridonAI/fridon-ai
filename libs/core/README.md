# FridonAI Core


FridonAI Core is the foundational package for building AI-driven chatbot platforms, specifically designed for the crypto world. It provides a modular and extensible architecture for creating powerful, domain-specific AI assistants.

## Features

- **Modular Plugin Architecture**: Easily extend functionality through a well-structured plugin system.
- **Dynamic Request Routing**: Efficiently navigate user requests to relevant plugins.
- **Blockchain Utilities**: Built-in support for blockchain-related operations.

## Installation

Install the package using pip:

```bash
pip install fridonai-core
```

## Usage

Here's a basic example of how to use FridonAI Core components:

```python
from fridonai_core.plugins import BasePlugin, BaseToolInput
from fridonai_core.plugins.utilities import BaseUtility
from fridonai_core.plugins.tools import BaseTool

from fridonai_core.graph import generate_response

class TestUtility(BaseUtility):
    async def arun(self, *args, **kwargs) -> str:
        return "You are the Superman!"
    
class TestToolInput(BaseToolInput):
    pass


TestTool = BaseTool(
    name="test-tool",
    description="Use this tool to answer any questions.",
    args_schema=TestToolInput,
    utility=TestUtility(),
    examples=[],
)

class TestPlugin(BasePlugin):
    name: str = "Test"
    description: str = "Use this plugin to answer any questions."
    tools: list[BaseTool] = [TestTool]


rs = await generate_response(
    "Who am I?", 
    plugins=[TestPlugin()], 
    memory='sqlite',
    config={"thread_id": "test"}, 
    return_used_agents=False
)
```

## Plugin Structure

FridonAI Core uses a hierarchical structure for plugins:

1. **Plugins**: Extend `BasePlugin`
2. **Tools**: Extend `BaseTool`
3. **Utilities**: Extend `BaseUtility`

Specialized utilities are available for specific use cases:
- `BlockchainUtility`: For blockchain operations
- `RemoteUtility`: For making remote API calls
- `LLMUtility`: For language model interactions

## Graph-based Processing

The core includes a Graph component that manages conversation flow and agent interactions. It's responsible for:

- Building networks of LLM Agents (Plugins)
- Routing messages between agents
- Managing agent states
- Creating chains with prompts and models
- Parsing outputs
- Composing independently implemented plugins

## Documentation

For more detailed usage instructions and API documentation, please visit our [main README](https://github.com/FridonAI/fridon-ai/blob/main/README.md).

## Contributing

We welcome contributions!

## Stay Connected

Follow us on Twitter for the latest updates and announcements:

[![Twitter Follow](https://img.shields.io/twitter/follow/FridonAI?style=social)](https://x.com/Fridon_AI)