# FridonAI

## Description

FridonAI is an artificial intelligence-driven chatbot platform specifically designed for the crypto world, particularly on Solana. Similar to how OpenAI's ChatGPT can converse on a variety of topics, FridonAI focuses on crypto, featuring targeted plugins for specific tasks such as swapping bitcoin to solana, analyzing solana charts, and providing coin recommendations. FridonAI serves as a comprehensive crypto assistant with domain-specific plugins.

## User Stories

- **Navigating the Plugins Marketplace**: Users can browse existing plugins, read descriptions and examples, see popularity and usage statistics, and select the desired plugins. For instance, users looking for coin price chart analysis can choose a relevant plugin, or if they want to swap coins easily via chat, they can select the Jupiter plugin. After subscribing to the chosen plugins, Fridon's capabilities are enhanced accordingly.
- **Enhanced Capabilities**: After acquiring plugins like "PriceChartAnalyzer" and "JupiterExecutor", users can command Fridon to analyze Bonk's last 30 days' price chart or swap 100 USDC to Bonk.
- **Creating Custom Plugins**: Users can create their own plugins by submitting a pull request to the open-source project, implementing only the business logic. FridonAI handles everything else, and the AI workflow will automatically determine if a query should be directed to the new plugin. Users set their own plugin prices, descriptions, and logos. FridonAI charges a 1% fee from each subscription.
- **Scoring System**: Every interaction with Fridon is scored. Repetitive questions receive lower scores, while sophisticated questions and effective use of plugins earn higher scores. These scores contribute to a leaderboard, with monthly opportunities for prizes from generated fees. Plugin creators also earn static points.

## Plugins

### Types of Plugins

- **Subscription-Based Plugins**: Accessible to users who pay for a subscription. Users can choose various subscription periods and renew them as needed.
- **NFT-Based Plugins**: Limited availability plugins accessed through NFTs. Users can mint new Plugin NFTs or use existing NFT collections to access functionalities.

### Existing Plugins

- **General Solana-Bonk Educational Plugin**: Learn about the Solana ecosystem with examples from BONK projects. Ask about staking, swapping, and more with specific project examples.
- **Blockchain Operations**: Perform operations like transferring tokens, getting token balances, supplying, borrowing, withdrawing, repaying, and getting balances.
- **Coin Price Technical Analysis**: Calculate indicators and generate detailed analyses for coin price charts.
- **Coin Searcher Plugins**: Find coins similar to others based on price charts or technical indicators. E.g., "Give me coins similar to SOL in December 2023."
- **Technical Analysis Notifier**: Receive notifications about promising coins based on technical analysis.

### Upcoming Plugins

- **Coin Sniper**: Identify promising freshly launched tokens using machine learning. Users receive detailed explanations of why certain coins are considered promising.
- **Personalized Signal Notifier**: Set custom alerts for specific coin conditions and receive notifications as per user-defined criteria.
- **Blockchain Protocols Recommender**: Get personalized recommendations based on wallet contents, such as staking or moving assets for higher APY.
- **Trader**: Analyze coins as famous traders do, with automated trading strategies from multiple perspectives like Emperor Trader and Fridon Trader.

## Integration and Community

### Fridon Assistant Integration / Chat Providing

Integrate Fridon on your platform using an API_KEY to leverage subscribed plugins. This allows seamless usage of Fridon's capabilities across various platforms.

### Community

- **Assistant Users**: Individuals who subscribe to and use desired plugins.
- **Plugin Contributors**: Developers who create and contribute plugins, enhancing Fridon's capabilities with blockchain operations, AI analytics, social network integrations, and more.

## Advantages

- **Open-Source**: Anyone can enhance Fridon's capabilities by implementing plugin business logic without understanding the entire infrastructure.
- **Income Opportunities**: Create innovative plugins to earn money, with generated fees distributed to loyal users based on earned scores.
- **NFT Utilization**: Plugins based on NFTs provide new utilities, increasing their value and tradability.
- **Collaboration with NFT Creators**: Partner with NFT creators to develop plugins accessible to their NFT holders.
- **AI Capabilities**: Fridon uses AI to generate responses and decide which plugins to use, creating complex AI plugins for various tasks like coin price analysis, market recommendations, and automated trading.
- **Convenient Environment**: A unified platform to handle all crypto-related activities on Solana with a simple UI/UX.

## Future Enhancements

- **NFT-Based Plugins**: Link plugins to existing NFTs or create new NFT collections for plugins.
- **Advanced AI Plugins**: Develop plugins like Coin Sniper, Personalized Signal Notifier, and Blockchain Protocols Recommender.
- **Improved Query Handling**: Enhance the AI's ability to handle complex and multiple queries simultaneously.
- **UI/UX Improvements**: Continuously refine the user interface and experience.

