
from agents import Agent, Runner, trace, function_tool, gen_trace_id, ModelSettings
from search_agent import search_agent
from planner_agent import planner_agent
from writer_agent import writer_agent
from email_agent import email_agent
from clarifying_agent import clarifying_agent
import asyncio


class AgenticResearchManager:
    instructions = """You are an autonomous researcher. Given a query, your role is to take out a deep research and get a comprehensive report using all available tools.\
        First, come up with a list of clarifying questions that can help understand the query better using the clarifying_agent tool.\
        Then use the planner_agent tool to come up with a search plan based on the query and the list of clarifying questions generated in the steps above.\
        When the search plan is ready, use the search_agent tool to perform web searches.\
        When the web searches are done, use the writer_agent tool to generate a comprehensive report.\
        When the report is ready, you will send an email to the user with the report by using the email sending handoff.\
        """

    tool1 = clarifying_agent.as_tool(tool_name="clarifying_agent", tool_description="Use this tool to come up with a list of clarifying questions that can help understand the query better.")
    tool2 = planner_agent.as_tool(tool_name="planner_agent", tool_description="Use this tool to come up with a search plan based on the query and clarifying questions.")
    tool3 = search_agent.as_tool(tool_name="search_agent", tool_description="Use this tool to perform web searches.")
    tool4 = writer_agent.as_tool(tool_name="writer_agent", tool_description="Use this tool to generate a comprehensive report.")

    tools = [tool1, tool2, tool3, tool4]
    handoffs = [email_agent]

    research_agent = Agent(
        name="Agentic Research Manager",
        instructions=instructions,
        tools=tools,
        handoffs=handoffs,
        model="gpt-4o-mini",
        model_settings=ModelSettings(tool_choice="required"),
        )

