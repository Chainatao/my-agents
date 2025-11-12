from agents import Agent, ModelSettings
from pydantic import BaseModel, Field

QUESTIONS_NUMBER = 3

INSTRUCTIONS = "Given a query, your role is to come up with {QUESTIONS_NUMBER} clarifying questions that can help understand the query better. Use the yield_progress tool to record the progress. Output a list of clarifying questions."

class ClarificationQuestion(BaseModel):
    reason: str = Field(description="Your reasoning for why this question is important to the query.")
    question: str = Field(description="A very relevant to the query clarifying question which could be used to better understand the query.")


class QuestionsList(BaseModel):
    questions: list[ClarificationQuestion] = Field(description="A list with clarifying questions to better understand the query.")
    

clarifying_agent = Agent(
    name="ClaryfingAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=QuestionsList,
    model_settings=ModelSettings()
)