from libs.internals.scoring.chain import ScorerChain

scorer_chain = ScorerChain()

async def calculate_score(user_message, response, used_agents, old_user_messages) -> int:
    score = await scorer_chain.arun(user_message, old_user_messages, response)
    return score
