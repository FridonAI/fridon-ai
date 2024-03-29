from semantic_router import Route
from semantic_router.layer import RouteLayer
from semantic_router.encoders import OpenAIEncoder

defi_stake_borrow_lend_route = Route(
    name="DefiStakeBorrowLend",
    utterances=[
        "I want to stake 100 pyth on pyth governance",
        "Please borrow 100 usdc on Kamino",
        "Lend 100 bonk on Marginify",
        "I want to stake 100 jup on jupiter",
        "Please lend 1123 jup on Kamino",
        "Withdraw 0.01 sol from Kamino",
        "Repay 123 usdc on Kamino",
        "Deposit 100 bonk on Marginify",
        "Supply 10000 dfl on Kamino",
    ]
)

defi_balance = Route(
    name="DeFiBalance",
    utterances=[
        "Can you tell me my sol balance?",
        "What is my lending usdc balance on Kamino?",
        "How much bonk I've borrowed on Marginify?",
        "Can you tell me my staked jup balance on jup governance?",
        "how much jup do I have on kamino lending?",
        "How much usdt is borrowed on Kamino?",
        "How much sol is borrowed on my Kamino account?",
        "How much WIF do I have deposited on kamino?",
    ]
)

defi_transfer = Route(
    name="DeFiTransfer",
    utterances=[
        "Transfer 100 sol to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
        "Send 100 usdc to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
        "Please, send 100 bonk to ArSZESuVtg5ac7vN8mqmUUgi8Sn8HVh46vq3KmZ86UBY",
        "Send 10 dfl to drakula.sol",
        "I want to transfer 10000000 dfl to abcde.sol",
        "Let's send 1000 pyth to 3bNVe2bKqazEnFZjmLegdwCWkANDXoUKdAMvTcL4AV4P",
    ]
)


defi_talker = Route(
    name="DeFiTalker",
    utterances=[
        "How are you?",
        "Who are you?"
        "What is DeFi?",
        "What is your project about?",
        "For what can I use Kamino?",
        "What is the purpose of Marginify?",
        "What is SPL token?",
        "Tell me about Pyth network",
        "What features your product has?",
        "What is Kamino?",
        "What is the purpose of Jupiter?",
        "How can I use landing on Kamino?",
        "What does pyth do?",
    ]
)


defi_news = Route(
    name="News",
    utterances=[
        "What is the latest news on my followed Discords?",
        "Summarize the latest news on my Defiland's announcements",
        "What is the today's news on Twitter?",
    ]
)


coin_search = Route(
    name="CoinSearch",
    utterances=[
        "Give me list of coins which are in top 100 and are AI based.",
        "Find coins which have the same chart as Wif between 1-25 Dec 2023.",
        "Search for coins which have bullish divergence and are in top 100 market cap.",
        "Give me coins from solana ecosystem which are in top 100 market cap.",
        "What coins are similar to rndr?",
        "Which coins have AI product?",
    ]
)

discord_action = Route(
    name="DiscordAction",
    utterances=[
        "Follow Solana's server on Discord, please.",
        "Unfollow Tensorians' server on Discord.",
        "Follow Madlad's server on Discord.",
        "Unfollow OkayBear's server on Discord.",
        "Follow bonk please",
        "Unfollow bonk please",
    ]
)


routes = [
    defi_stake_borrow_lend_route,
    defi_balance,
    defi_talker,
    defi_news,
    defi_transfer,
    coin_search,
    discord_action,
]

rl = RouteLayer(encoder=OpenAIEncoder(), routes=routes)


def get_category(query):
    print("Get Category", query['query'])
    category = rl(query['query']).name
    print("Category", category)
    return category
