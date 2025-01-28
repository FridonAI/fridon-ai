from libs.internals.scoring import calculate_score


class CalculateUserMessageScoreService:
    async def process(
        self,
        wallet_id: str,
        user_message: str,
        response: str,
        used_agents: list[str],
        prev_user_messages: list[str] = [],
    ):
        score = await calculate_score(
            user_message, response, used_agents, prev_user_messages
        )
        return score
