# FridonAI

FridonAI is an open-source project dedicated to enhancing the cryptocurrency experience through AI-powered tools and services. By combining intelligent analytics, powerful search capabilities, and real-time notifications within a cohesive chat interface, FridonAI simplifies complex blockchain interactions and provides insightful analytics using natural language commands.

## Table of Contents

- [Introduction](#introduction)
- [Products](#products)
  - [FridonAnalytics](#fridonanalytics)
  - [FridonSearch](#fridonsearch)
  - [FridonNotifier](#fridonnotifier)
  - [FridonBlockchain](#fridonblockchain)
  - [FridonChat](#fridonchat)
- [Open Source Structure](#open-source-structure)
  - [Apps](#apps)
  - [Libs](#libs)
- [Developer Opportunities](#developer-opportunities)
- [Platform Access](#platform-access)
- [User Experience](#user-experience)
- [Problems FridonAI Solves](#problems-fridonai-solves)
- [One-Liner Description](#one-liner-description)
- [Two-Liner Description](#two-liner-description)
- [Three-Liner Description](#three-liner-description)
- [Paragraph Description](#paragraph-description)
- [Conclusion](#conclusion)

## Introduction

FridonAI leverages artificial intelligence to enhance the crypto experience, offering a suite of tools and services for cryptocurrency analysis, blockchain operations, and more. The platform's mission is to simplify complex blockchain interactions and provide insightful analytics through an intuitive chat interface with an assistant named Fridon.

## Products

### FridonAnalytics

Offers a suite of tools to help users analyze cryptocurrencies:

- **Coin Price Analytics**: Analyze the performance of a coin's price chart using various indicators and visualize it.

  - *Example Command*: "Analyze SOL 1h price chart for me"

- **TextToDiagram**: Generate visualizations for specific coins based on text input.

  - *Example Command*: "Give me BTC 1h price chart with MACD and support resistances."

- **TraderCloner**: Emulate the analysis methods of top traders by integrating their open-source strategies. (Upcoming feature)

  - *Example Command*: "Give me SOLANA analytics as Emperor would do"

- **Coin Trust**: the platform will utilize AI and Graph Neural Networks to predict the trustworthiness of new coins, helping users make informed investment decisions. (Upcoming feature)


- **Coin Recommendation System**: Recommend coins purchased by wallets that exhibit similar behavior to yours. (Upcoming feature)

### FridonSearch

Enables advanced AI-driven coin searches:

- **Technical Coin Searcher**: Find coins using textual descriptions, technical indicators, patterns, and setups.

  - *Example Command*: "Give me coins with bullish divergence with market cap > $2B and currently crossed 1h resistance."

- **Coin Chart Similarity Search**: Discover coins with price charts similar to a given example using a pre-trained time series model.

  - *Example Command*: "Give me coins with the same chart as Solana had 3 months ago."

- **Past Chart Similar Coins Search**: Find coins in the past that look the same as the current coin. (Upcoming feature)

  - *Example Command*: "Give me coins which were like SOL in the past"

- **TraderSearcher**: Identify coins that would be considered promising by specific traders. (Upcoming feature)

  - *Example Command*: "Find coins that look promising to Emperor."

### FridonNotifier

Allows users to create custom notifications:

- **Custom Coin Indicator Notifier**: Set up notifications based on specific indicators and textual descriptions.

  - *Example Command*: "Notify me when Solana breaks $145 resistance and MACD reaches 140."

- **Trader Notifier**: Get notified when a specific trader would consider a coin bullish and recommend buying. (Upcoming feature)

### FridonBlockchain

Enables blockchain operations through simple text commands:

- **Educational Queries**:

  - *Example Command*: "What's swap and what platforms can I use for it?"

  - *Example Command*: "Can you suggest staking platforms where I can stake my Solana?"

- **Account Queries**:

  - *Example Command*: "What's my BONK balance?"

- **Transaction Execution**:

  - *Example Command*: "Swap 10 USDC to SOL."

### FridonChat

Unifies all products via a chat interface. Users interact with the Fridon assistant, which automatically decides which products and functionalities to use, treating each as a plugin.

- **Open-Source Chat Pipeline**: Built and open-sourced the entire chat pipeline, welcoming community contributions. Contributors can create new blockchain plugins, support different DeFi protocols, add staking or borrowing functionalities, and more, following our guidelines.

- **FridonAI-Core Package**: The chat's core package, `fridonai-core`, is available for everyone to install (`pip install fridonai-core`). It allows developers to write their own plugins and integrate them into their chat applications, simplifying the implementation of blockchain-based analytics and notification plugins.

- **FridonAI-Community Package**: Implemented plugins, tools, and utilities are also available for developers by installing (`pip install fridonai-community`). (Upcoming feature)


## Plugins System

FridonAI operates on a plugin-based architecture where each functionality is encapsulated as a plugin. Plugins are modular components that extend Fridon's capabilities, ranging from cryptocurrency analytics to blockchain operations.

### How Plugins Work
- Each plugin adds specific capabilities to Fridon's chat interface
- Without subscribing to a plugin, Fridon cannot access that plugin's features
- Users can mix and match plugins based on their needs
- Plugin creators can monetize their contributions through the subscription model

Some plugins are free and included by default, while others require a subscription and monthly payment.


### Apps

The `apps` directory contains application services that allow users to deploy the entire application with its backend, data flow, and more.

- **fridon_backend**: A Nest.js backend application that handles wallet connections, blockchain transaction generation, sending and signing transactions, subscription to specific plugins, score calculations, leaderboard updates, chat message storage, and more.

- **fridon_brain**: A Python application responsible for processing user messages and generating responses using the Libs package. The `fridon_backend` uses this application to generate replies to user messages.

- **fridon_crone**: Used for cron jobs, mainly for data fetching, aggregation, calculations, and so on (e.g., fetching coin prices and additional data hourly).

### Libs

The `libs` directory is the core of the project, consisting of:

- **Core**: A foundational package for building AI-driven chatbots. It provides a generic workflow that diversifies the chatbot's capabilities, automatically deciding which functionalities to invoke based on user messages, determining response formats, and updating messaging states. Contributors can easily create their own plugins by extending the base functionalities offered by the Core package.

  - The Core package is independently published and can be installed via pip (`pip install fridonai-core`). For more information, visit the GitHub repository.

- **Community**: A space where actual plugins are implemented by both our team and open-source contributors. This will also be published as an independent package (`pip install fridonai-community`).

- **Additional Packages**: Other packages in `libs` handle data management, storing and querying coin prices, indicators, fetching data from providers like Birdeye and Binance, and a scoring system that calculates personalized scores based on user interactions.


## Open Source Structure

FridonAI is entirely open-source, and the full codebase is available on GitHub. The project is organized into two main parts: Apps and Libs.

## Developer Opportunities

FridonAI offers developers the chance to:

- **Contribute to Our Open-Source Project**: Create plugins that other users can utilize on our platform (fridon.ai). Developers can choose to offer their plugins for free or charge subscribers a monthly fee.

- **Integrate Our Functionality into Your Projects**: Install our packages (`fridonai-core` and `fridonai-community`) in your own projects and implement custom plugins or use existing ones without worrying about the complexities of AI and large language model (LLM) integration.

## Platform Access

Our platform is accessible at [https://www.fridon.ai/](https://www.fridon.ai/), where users can explore and use the plugins they need.

## User Experience

Here's how users interact with the FridonAI platform:

1. **Plugins Marketplace**: Users can browse the marketplace to view existing plugins, read descriptions, see examples, check popularity, and view usage statistics.

2. **Selecting Plugins**: Based on their needs, users can choose the required plugins. For example, to perform coin price chart analysis, users can select a relevant plugin; to swap coins easily via chat, they can select a Jupiter plugin. After choosing the plugins, users can subscribe for several months and pay accordingly.

3. **Enhanced Capabilities**: Once users acquire plugins, their assistant Fridon's capabilities are expanded. For instance, after obtaining the "PriceChartAnalyzer" and "JupiterExecutor" plugins, Fridon can handle requests like:

   - "Analyze BONK's last 30 days' price chart, please."
   - "Fridon, swap 100 USDC to BONK."

4. **Creating Custom Plugins**: Users can create their own plugins by submitting a pull request to our open-source project. By implementing the business logic, everything else is automatically managed, and our AI workflow will determine if user queries pertain to the new plugin. Users can set the price, name, description, type, and logo for their plugins.

5. **Scoring System**: Each time a user interacts with Fridon, our AI system assigns a score based on the quality of the interaction. Repetitive questions yield lower scores, while sophisticated and diverse interactions earn higher scores. These scores contribute to both the user and the plugin creator. Scores are reflected on a leaderboard, and each month, top performers have the opportunity to receive prizes from generated fees. Leaderboard metrics include total scores, number of plugins created, number of plugin calls made, and how many times a user's plugins were utilized.

## Problems FridonAI Solves

- **Simplifies Cryptocurrency Analysis**: Analyzing cryptocurrency price charts often requires specialized knowledge and tools. FridonAI simplifies this process with intuitive features like Coin Price Analytics and TextToDiagram, allowing users to analyze and visualize coin performance using natural language commands.

- **Advanced Coin Search**: Finding coins based on specific technical indicators or chart patterns has been cumbersome. With FridonSearch's Technical Coin Searcher, users can find coins through detailed textual descriptions. The Coin Chart Similarity Search discovers coins with similar historical or current chart patterns using pre-trained time series models.

- **Real-Time Notifications**: Missing trading opportunities due to lack of real-time notifications is a common issue. FridonNotifier enables users to set up custom notifications for specific indicators and scenarios, ensuring they stay informed of important market changes.

- **Simplified Blockchain Operations**: Executing blockchain operations often requires technical expertise, posing a barrier to many users. FridonBlockchain simplifies blockchain interactions through natural language commands, enabling users to perform operations like swapping tokens or checking balances effortlessly.

- **Community Contribution**: Addresses the limited community contribution in crypto tools. By open-sourcing the chat pipeline and providing the FridonAI-Core and FridonAI-Community packages, FridonAI encourages community contributions and makes it easier for developers to create and integrate new plugins and functionalities.

- **Educational Assistance in DeFi**: Helps users overcome barriers to learning and utilizing DeFi protocols. Through educational and practical assistance in FridonBlockchain and FridonChat, users are guided through DeFi operations like staking and swapping via simple text commands.

### Upcoming Functionalities

- **Coin Trust Score**: FridonAI plans to tackle the risk of investing in untrustworthy or scam coins. With Coin Trust Score, the platform will utilize AI and Graph Neural Networks to predict the trustworthiness of new coins, helping users make informed investment decisions.

- **Automated Trading Strategies**: Introducing Trader Notifier and TraderSearcher, which will notify users when coins meet criteria that specific traders would find promising, allowing for automation of personalized trading strategies.



## List of Descriptions

Empowering Crypto with AI-Powered Insights and Seamless Interactions

### One-Liner Description

FridonAI leverages AI to enhance the crypto experience, combining intelligent analytics, powerful search, and real-time notifications within a cohesive chat interface.

### Two-Liner Description

FridonAI leverages AI to enhance the crypto experience, combining intelligent analytics, powerful search, and real-time notifications within a cohesive chat interface. Gain insightful analytics and simplify complex blockchain interactions through intuitive, natural language commands.

### Three-Liner Description

FridonAI leverages AI to enhance the crypto experience, combining intelligent analytics, powerful search, and real-time notifications within a cohesive chat interface. Our platform offers insightful analytics and powerful search tools, simplifying complex blockchain interactions using natural language commands. Empowering users to analyze cryptocurrencies, execute blockchain operations, and stay informed effortlessly.

### Paragraph Description

FridonAI leverages AI to enhance the crypto experience, combining intelligent analytics, powerful search, and real-time notifications within a cohesive chat interface. Our open-source platform offers insightful cryptocurrency analytics and simplifies complex blockchain interactions through intuitive, natural language commands. With features like coin price analytics, advanced coin search, custom notifications, and simplified blockchain operations, FridonAI empowers users to make informed decisions effortlessly. By unifying these functionalities in a chat interface and promoting community contributions through open-source packages, we aim to revolutionize how users interact with the crypto world.


---

For more information, visit our [GitHub repository](https://github.com/FridonAI) or explore our platform at [https://www.fridon.ai/](https://www.fridon.ai/). [Twitter X](https://x.com/Fridon_AI)  

For all the links we've got: [Linktree](https://linktr.ee/fridonai)