from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from fridonai_core.graph.models import get_model
from pydantic import BaseModel, Field

from settings import settings

prompt = PromptTemplate.from_template("""\
You are expert in assessing user's chat with assistant. You have to assign score to user's current message from 0 to 1.\

Past several messages of user and assistant response on the last message are given.

There are several things to take into account:

1. If user is abusing the chat the score should be near to 0. You have to use last messages for this.
2. More diverse user's messages, used agents higher score should be.
3. If assistant message says that user's request couldn't be done, you should assign score to 0.
4. If user asks same question but different parameters don't count it as abuse. (e.g. "What is the price of BTC?" and "What is the price of ETH?")
5. Max 1 point if for for diverse, interesting dialogue with Fridon and using different agents.
6. If the question is legit and not spam and isn't perfect as well, generate score from {min} to {max} considering how complex the latest q/a is how many agents are used. For each agent you have to write corresponding score and finally sum them up.


<user_current_message>
{user_message}
</user_current_message>

<assistant_response>
{assistant_response}
</assistant_response>
                                      
For checking if user is abusing the chat or assessing diversity of user's requests and how naturally FridonAI is used, you should use user's previous messages and agents already used during conversation.
                                      
<user_past_messages>
{past_messages}
</user_past_messages>

<used_agents>
{used_agents}
</used_agents>  
    
if past message is for solana_bonk_educator plugin and nor question nor its answer isn't about solana, bonk or solana specific domain score should be 0.
For each used agent you should write corresponding score considering question and answer and history, and finally generate their sum them. 

If assistant response is error score must be zero.                                  
""")

agent_to_score = {
    "intelligent-coin-searcher": 2,
    "coin-technical-analyzer": 2,
    "coin-observer": 1.5,
    "wallet": 1.5,
    "fridon": 0.3,
    "solana-bonk-educator": 0.5,
    "og-traders-simulator": 2,
    "off-topic": 0,
}


class ScoreOutput(BaseModel):
    "What score should be assigned to user's latest message and response."

    score: float | int = Field(description="Score for user's latest message")


class ScorerChain(BaseModel):
    structured_output: type[BaseModel] = ScoreOutput
    prompt: PromptTemplate = prompt

    @property
    def _chain(self) -> Runnable:
        return prompt | get_model("gpt-4o").with_structured_output(
            self.structured_output
        )

    async def arun(self, user_message, response, prev_user_messages, used_agents):
        total_score = 0
        for agent in used_agents:
            total_score += agent_to_score[agent]

        used_agents_with_scores = [
            {
                agent: {
                    "min_score": agent_to_score[agent] / 2,
                    "max_score": agent_to_score[agent],
                }
            }
            for agent in used_agents
        ]
        return (
            await self._chain.ainvoke(
                {
                    "past_messages": prev_user_messages,
                    "user_message": user_message,
                    "assistant_response": response,
                    "used_agents": used_agents_with_scores,
                    "max": total_score,
                    "min": total_score / 2,
                }
            )
        ).score

    class Config:
        arbitrary_types_allowed = True
