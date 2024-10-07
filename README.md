## What's FridonAI?

FridonAI is an open-source platform that delivers AI-powered tools, for cryptocurrency analysis and blockchain operations, all wrapped into an intuitive chat interface.

### Key Features

- **AI-Based Tools for Crypto**: FridonAI simplifies blockchain analysis and interactions with cutting-edge AI.
  - **FridonAnalytics**: Analyze cryptocurrency prices, visualize data, emulate top traders' strategies, predict coin risks, recommend coins, and analyze protocol churn.
  - **FridonSearch**: Search for coins based on technical indicators, price chart similarity, and emulate trader-specific searches.
  - **FridonNotifier**: Set up custom alerts and notifications based on personalized indicators, or mimic the actions of top traders.
  - **FridonBlockchain**: Interact with blockchain operations effortlessly using simple text commands.
  - **FridonChat**: The core chat interface that unifies all functionalities under a single chat experience, where each capability is treated as a plugin.

- **Open-Source**
  - **Libraries**: Create your own crypto-focused chatbot using [fridon-core](/libs/core/), or leverage community-implemented tools available in [fridon-community](/libs/community/).
  - **End to End Application**: Except for the core chat functionality, the whole application is open-sourced. You can run your own instance of FridonAI and modify it according to your needs.
  - **Contribute**: Help diversify FridonAI's tools and capabilities through community contributions.

- **Platform**
  - **Empower Everyone**: Whether you are a user looking to utilize AI-driven tools or a developer looking to earn money from your custom tools, FridonAI makes it possible through its easy-to-use platform.


## How Does It Help?

- **Build Your Custom AI Chat**: Implement your own tools, and let [fridon-core](/libs/core/) manage everything else for your custom AI chatbot.

- **Use Implemented Crypto Tools**: Get access to powerful crypto tools or extend their capabilities by adding your custom features with [fridon-community](/libs/community/).

- **Chat to Unlock FridonAI's Potential**: Through the FridonAI platform, you can interact with all of FridonAI's capabilities effortlessly—just by chatting.



## Getting Started


**Use fridon-core as a library**
```bash
pip install fridonai-core
```
[fridonai-core documentation](libs/core/README.md)


**Run the whole project with Docker Compose**

```bash
docker compose up --build
```

**Set up the FridonAI Brain locally**

*It will need Redis and Postgres to be runnning and configured in .env*
1. **Clone the Repository**

   ```bash
   git clone https://github.com/FridonAI/fridon-ai.git
   ```

2. **Install Dependencies**

   ```bash
   poetry lock --no-update
   poetry install --no-root
   ```

3. **Set Up Environment Variables**

   Create a `.env` file in the `apps/fridon_brain` directory and add the necessary variables as defined in [`settings.py`](settings.py) or in [`.env.example`](apps/fridon_brain/.env.example)

4. **Run the Application**

   ```bash
   poetry run python -u -m apps.fridon_brain.main
   ```

## Future Plans
- Different api technology support
- Detailed documentation
- More plugins


## Contribution

We welcome contributions from the community. Developers can create new plugins or improve existing ones to enhance FridonAI's capabilities.

## License

This project is open-source and available under the [MIT License](LICENSE).


## Stay Connected

Follow us on Twitter for the latest updates and announcements:

[![Twitter Follow](https://img.shields.io/twitter/follow/FridonAI?style=social)](https://x.com/Fridon_AI)

---

*Note: For more detailed information, please refer to the codebase and inline documentation.*