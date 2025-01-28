from libs.internals.scoring.chain import ScorerChain

scorer_chain = ScorerChain()

async def calculate_score(
    user_message, response, used_agents, prev_user_messages
) -> int:
    score = await scorer_chain.arun(
        user_message, response, prev_user_messages, used_agents
    )
    return score
