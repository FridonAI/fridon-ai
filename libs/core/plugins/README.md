# Plugins System

Plugins in FridonAI are powerful, domain-specific modules that extend the core functionality of the AI assistant. They are designed to handle particular tasks of domain, leveraging a combination of Tools and Utilities to process user requests and provide specialized responses.

## Plugin Structure

A plugin is essentially an LLM (Large Language Model) Agent that performs specific tasks using a set of Tools. The structure of a plugin is hierarchical:

1. **Plugin**: Extends `BasePlugin`
2. **Tools**: Extend `BaseTool`
3. **Utilities**: Extend `BaseUtility`

This structure allows for easy development and integration of new functionalities into the FridonAI system.

## Key Components

### BasePlugin

The `BasePlugin` class is the foundation for all plugins. It defines the basic structure and properties that all plugins should have.

### BaseTool

The `BaseTool` class extends LangChain's `BaseTool` and provides a wrapper around Utilities to make them compatible with the LangChain framework.

### BaseUtility

The `BaseUtility` class is the base class for all utilities, which implement the core business logic of the plugin.

## Specialized Utilities

FridonAI provides several specialized utility classes to simplify common tasks:

### RemoteUtility

The `RemoteUtility` class is designed for making remote API calls. When extending this class, you only need to implement the `_arun` method to return the request body. The utility will automatically handle sending the request and processing the response.

### BlockchainUtility

The `BlockchainUtility` class handles complex blockchain operations, such as generating transactions, sending them for user signing, and waiting for completion. It abstracts away the complexities of blockchain interactions.

### LLMUtility

The `LLMUtility` class simplifies interactions with language models. You can define the LLM's task description and desired output structure, and the utility handles the rest.

## Developing Plugins

When developing a new plugin:

1. Create a new directory in `libs/community/plugins/` for your plugin.
2. Extend the appropriate base classes (`BasePlugin`, `BaseTool`, `BaseUtility`).
3. Implement the required methods and properties.
4. Use specialized utilities where appropriate to simplify development.

For examples of plugin implementation, refer to the existing plugins in the [`libs/community/plugins/`](../../community/plugins/) directory.

## Plugin Registry

Plugins are managed through a `PluginRegistry` class, which handles plugin registration and retrieval.

## Conclusion

The plugin system in FridonAI provides a flexible and extensible architecture for adding new functionalities. By leveraging the provided base classes and specialized utilities, developers can easily create powerful, domain-specific plugins that enhance the capabilities of the AI assistant.