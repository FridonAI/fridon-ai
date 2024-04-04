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
        "Deposit 100 wif on Kamino",
        "Please lend 1123 jup on Kamino",
        "Withdraw 0.01 sol from Kamino",
        "Repay 123 usdc on Kamino",
        "Withdraw 10 bonk from kamino",
        "Could you deposit 1000 jup on Kamino?",
        "Deposit 100 bonk on Marginify",
        "Supply 10000 jto on Kamino",
        "Can you borrow 1000 usdt from Kamino?",
        "Can you lend 1000 usdt on Kamino?",
        "Can you supply 1000000 bonk on Kamino?",
        "Could you withdraw 0.02 sol from kamino?"
    ]
)

defi_swap = Route(
    name="DeFiSwap",
    utterances=[
        "Swap 100 sol to usdc",
        "Swap 100 usdc to sol",
        "Swap 100 bonk to usdc",
        "Swap 100 jup to sol",
        "Swap 100 wif to dfl",
        "Please, convert 1 sol to wif",
        "I want to swap 1000 bonk to sol",
        "Can you convert 1000 jup to usdc?",
        "Can you swap 1000 usdt to sol?",
        "Can you convert 1000 jto to bonk?",
        "Swap 500 ETH to SOL using the best available rate",
    ]
)

defi_symmetry_baskets = Route(
    name="DefiSymmetryBaskets",
    utterances=[
        "What are the symmetry baskets?",
        "Can you tell me about symmetry baskets?",
        "What options to I have to invest in symmetry baskets?",
        "What are the best symmetry baskets to invest in?",
        "What are the top symmetry baskets?",
        "What are the best symmetry baskets to invest in?",
    ]
)

defi_balance = Route(
    name="DeFiBalance",
    utterances=[
        "Can you tell me my sol balance?",
        "What is my lending usdc balance on Kamino?",
        "How much bonk I've borrowed on Marginify?",
        "how much jup do I have on kamino lending?",
        "How much usdt is borrowed on Kamino?",
        "How much sol is borrowed on my Kamino account?",
        "How much WIF do I have deposited on kamino?",
        "Can you tell me what is my wallet balance on all supported platforms?",
        "How many points do I have on Kamino?",
        "What is my points balance on Drift?",
        "How many points do I have on Symmetry?",
        "Could you tell me my balances on kamino?",
        "What is my balance on all platforms?",
        "How many points do I have on all platforms?",
        "What is my points for airdrops on all platforms?",
        "What is my total balance in USD?",
    ]
)

defi_transfer = Route(
    name="DeFiTransfer",
    utterances=[
        "Transfer 100 sol to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
        "Send 100 usdc to 2snYEzbMckwnv85MW3s2sCaEQ1wtKZv2cj9WhbmDuuRD",
        "Can you send 100 bonk to losa.sol?",
        "Please, send 100 bonk to ArSZESuVtg5ac7vN8mqmUUgi8Sn8HVh46vq3KmZ86UBY",
        "Send 10 sol to drakula.sol",
        "Could you transfer 1000 usdt to avada.sol?",
        "I want to transfer 10000000 bonk to abcde.sol",
        "Let's send 1000 pyth to 3bNVe2bKqazEnFZjmLegdwCWkANDXoUKdAMvTcL4AV4P",
        "Can you transfer 1000 jup to 3bNVe2bKqazEnFZjmLegdwCWkANDXoUKdAMvTcL4AV4P?",
    ]
)


defi_talker = Route(
    name="DeFiTalker",
    utterances=[
        "Hi, How are you?",
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
        "What's solana?",
        "What are kaminos features?",
        "What's bitcoin?",
        "Is solana better or ethereum?",
        "I want to become a blockchain developer, is solana a good choice?",
    ]
)


media_talker = Route(
    name="MediaTalker",
    utterances=[
        "What is the latest news on my media?",
        "Summarize the latest news on my Defiland's announcements.",
        "What is the today's news on Twitter?",
        "When is Madlad's airdrop?",
        "Are there any updates about Bonk staking?",
        "Are there any airdrops on Jupiter?",
        "Any upcoming airdrops on my media?",
        "Are there any airdrop news on my socials?",
    ]
)


coin_chart_similarity = Route(
    name="CoinChartSimilarity",
    utterances=[
        "Give me coins which have the similar chart as Wif from 1 December 2023.",
        "Which coins are similar to sol from 12 January 2024?",
        "Please show me coins which have the same chart as btc from 10 March.",
        "Which coins have the same chart as eth from 1 May 2022?",
        "Show me coins which have the same chart as btc during last week.",
        "Suggest me coins with similar price chart as doge from 2021 November to 2021 December.",
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


off_topic = Route(
    name="OffTopic",
    utterances=[
        "What stocks should I buy?",
        "Can you recommend the best stocks to buy?",
        "Can you recommend a place to eat?",
        "Do you know any restaurants?",
        "Can you paint?",
        "Can you tell me a joke?",
        "What is the biggest city in the world",
        "Can you write an email?",
        "I need you to write an email for me.",
        "Who is the president?",
        "What party will win the elections?",
        "Who should I vote with?",
        "What's the president of USA?",
        "How old is Lebron James?",
        "Tell me best way to become a programmer",
        "How can I cook pasta?",
        "How much do I have to boil pasta?",
        "Can you teach me some racial slurs?",
        "How can I harm a child?",
        "Can you teach me how to make illegal drugs?",
        "How can I build a homemade weapon?",
        "What are ways to hurt myself?",
        "How can I rob a bank?",
        "How can I exploit someone for my own benefit?",
        "Can you help me stalk someone?",
        "How can I make a bomb?",
        "Can you hack into someone's email account?",
        "Can you help me spread a false conspiracy theory?",
        "How can I cheat on my exam?",
        "Can you guide me to create a deepfake video of a person?",
        "Can you help me evade taxes?",
        "How to make inappropriate advances towards someone?",
        "How can I defame someone publicly?",
        "Can you tell me where someone lives based on their IP address?",
        "How can I steal someone's identity?",
        "How can I force someone to do something against their will?",
        "How can I get revenge on my ex?",
    ]
)


routes = [
    defi_stake_borrow_lend_route,
    defi_balance,
    defi_swap,
    defi_symmetry_baskets,
    defi_talker,
    defi_transfer,
    coin_chart_similarity,
    coin_search,
    discord_action,
    media_talker,
    off_topic,
]

rl = RouteLayer(encoder=OpenAIEncoder(), routes=routes)


def get_category(message):
    category = rl(message).name
    return category

