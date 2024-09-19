# What is FridonAI

FridonAI is an artificial intelligence-driven chatbot platform specifically designed for the crypto world, particularly on the Solana blockchain. Featuring targeted plugins for specific tasks such as swapping USDC to Solana, analyzing coin charts, providing coin search, and more. FridonAI serves as a comprehensive crypto assistant with domain-specific plugins.

## Features

### Plugins

FridonAI's functionality is extended through a variety of plugins, which can be either subscription-based or NFT-based.

**Types of Plugins:**

- **Subscription-Based Plugins**: Accessible to users who pay for a subscription. Users can choose various subscription periods and renew them as needed.
- **NFT-Based Plugins**: Limited availability plugins accessed through NFTs. Users can mint new Plugin NFTs or use existing NFT collections to access functionalities.

**Existing Plugins:**

- **General Solana-Bonk Educational Plugin**: Learn about the Solana ecosystem with examples from BONK projects. Ask about staking, swapping, and more with specific project examples.
- **Blockchain Operations**: Perform operations like transferring tokens, getting token balances, supplying, borrowing, withdrawing, repaying, and retrieving balances.
- **Coin Price Technical Analysis**: Calculate indicators and generate detailed analyses for coin price charts.
- **Coin Searcher Plugins**: Find coins similar to others based on price charts or technical indicators.
- **Technical Analysis Notifier**: Receive notifications about promising coins based on technical analysis.

**Upcoming Plugins:**

- **Coin Sniper**: Identify promising freshly launched tokens using machine learning.
- **Personalized Signal Notifier**: Set custom alerts for specific coin conditions and receive notifications as per user-defined criteria.
- **Blockchain Protocols Recommender**: Get personalized recommendations based on wallet contents, such as staking or moving assets for higher APY.
- **Trader**: Analyze coins as famous traders do, with automated trading strategies from multiple perspectives.

### Integration and Community

**Fridon Assistant Integration / Chat Providing**

Integrate FridonAI on your platform using an `API_KEY` to leverage subscribed plugins. This allows seamless usage of FridonAI's capabilities across various platforms.

**Community Participants:**

- **Assistant Users**: Individuals who subscribe to and use desired plugins.
- **Plugin Contributors**: Developers who create and contribute plugins, enhancing FridonAI's capabilities with blockchain operations, AI analytics, social network integrations, and more.

## Core Technical Overview

!!! Needs description of what this repository does

The core functionality of FridonAI is built with a modular architecture, allowing for easy integration and extension through plugins.


### What are Plugins?

Plugins in FridonAI are essentially LLM (Large Language Model) Agents that perform specific tasks using a set of Tools. Each plugin is designed to handle a particular domain or functionality.

- **Agents**: LLM-powered decision-makers that determine which Tools to use and in what order, based on the user's input and the task at hand.
- **Tools**: Functions that perform specific actions or retrieve information. They are wrappers around Utilities, adding functionality to make them compatible with LangChain's framework.
- **Utilities**: The underlying implementation of business logic and functionality that Tools utilize.

For more detailed information on LangChain Tools and Agents, refer to the [LangChain documentation](https://python.langchain.com/docs/modules/agents/).


### Plugin Structure and Development

At `app/core/plugins`, we've created an underlying structure of plugins, tools, and utilities to simplify plugin development. This structure allows users to extend base classes and implement only the business logic as utilities, while correctly setting parameters such as plugin name, utility description, examples, and so on.

The hierarchy is as follows:

1. **Plugins**: Extend `BasePlugin`
2. **Tools**: Extend `BaseTool`
3. **Utilities**: Extend `BaseUtility`

Developers can refer to the existing plugins in the `app/community/plugins/` directory for examples of how to implement new plugins.

There are several `BaseUtility` extensions available, which can be used depending on the utility's specific requirements:

- `BlockchainUtility`: For blockchain-related operations
- `RemoteUtility`: For making remote API calls
- `LLMUtility`: For language model interactions

By leveraging this structure, developers can focus on implementing the core functionality of their plugins without worrying about the underlying architecture.



### Put everything together

- **Graph**: Manages the conversation flow and agent interactions. Defined in [`app/core/graph/`](app/core/graph/), it uses LLM models to process user messages and delegate tasks to appropriate plugins. The Graph component is responsible for:
  - Dynamically building a network of LLM Agents, most of which are Plugins under the hood
  - Routing messages between agents
  - Managing states between agents
  - Creating chains with prompts and models
  - Parsing outputs
  - Automatically composing independently implemented plugins

  The Graph utilizes [LangGraph](https://github.com/langchain-ai/langgraph) (from LangChain) for graph structure and flow management, and [LangChain](https://github.com/langchain-ai/langchain) for chains, prompts, formatting, and other language model interactions. This architecture allows for a flexible and scalable system that can easily incorporate new plugins and functionalities.
![Graph](assets/graph.png)


### Application

- The application uses Redis extensively for message handling and communication:
  - Receiving messages from clients
  - Sending responses back to clients
  - Publishing updates and notifications
  - Inter-service communication

- You can see controller logic in `app/main.py` and service layer in `app/services`

- A separate [Nest.js application](https://github.com/FridonAI/api) has been built in a different repository, which interacts with this core Python backend. 


### Scoring

FridonAI implements a scoring system to incentivize user engagement and provide feedback on the quality of interactions. Here's how it works:

- After each user question or command is processed and answered, the system assesses the dialogue.
- The assessment focuses primarily on the latest question and answer pair.
- A score is generated based on this assessment, which reflects the quality and effectiveness of the interaction.
- This score is then sent to the API repository (separate from this core repository).
- The API stores the score and notifies the user of their earned points.

The exact scoring criteria and implementation details can be found in the relevant scoring module within the codebase. [Score Module](app/score)



## Getting Started

To set up the project locally:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/FridonAI/core.git
   ```

2. **Install Dependencies**

   ```bash
   poetry lock --no-update
   poetry install --no-root
   ```

3. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add the necessary variables as defined in [`app/settings.py`](app/settings.py) and in [`.env.example`](.env.example)

4. **Run the Application**

   ```bash
   poetry run python -u -m app.main
   ```

To set up the project with Docker, run:

```bash
docker build -t fridon-core .
docker run -p 8000:8000 fridon-core
```

## Future Plans
- Many interesting AI plugins 
- SDK to have core locally with just importing frodonai
- Different api technology support 

## Contribution

We welcome contributions from the community. Developers can create new plugins or improve existing ones to enhance FridonAI's capabilities.

## License

This project is open-source and available under the [MIT License](LICENSE).

---

*Note: For more detailed information, please refer to the codebase and inline documentation.*