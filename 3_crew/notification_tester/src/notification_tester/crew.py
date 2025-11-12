from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.push_tool import PushNotificationTool
from pydantic import BaseModel, Field
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


class JokeMessage(BaseModel):
    """ A company that is in the news and attracting attention """
    message: str = Field(description="Message to be sent to the user.")

@CrewBase
class NotificationTester():
    """NotificationTester crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
 
    @agent
    def joker(self) -> Agent:
        return Agent(config=self.agents_config['joker'], tools=[PushNotificationTool()])

    @task
    def joke(self) -> Task:
        return Task(
            config=self.tasks_config['tell_joke'], # type: ignore[index]
            output_pydantic=JokeMessage
        )


    @crew
    def crew(self) -> Crew:
        """Creates the NotificationTester crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
