import gradio as gr
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool, gen_trace_id, ModelSettings

from research_agent import AgenticResearchManager
from agents.lifecycle import RunHooks
import asyncio


class GradioRunHooks(RunHooks):
    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_agent_start(self, context, agent):
        await self.queue.put(f"[Agent Start] {agent.name}\n\n")

    async def on_tool_start(self, context, agent, tool):
        await self.queue.put(f"[Tool Start] {tool.name}\n\n")

    async def on_tool_end(self, context, agent, tool, result):
        await self.queue.put(f"[Tool End] {tool.name} -> {result}\n\n")

    async def on_handoff(self, context, from_agent, to_agent):
        await self.queue.put(f"[Handoff] {from_agent.name} -> {to_agent.name}\n\n")

    async def on_agent_end(self, context, agent, output):
        await self.queue.put(f"[Agent Finished] {output}\n\n")
        
load_dotenv(override=True)


async def run_query(query: str):

    trace_id = gen_trace_id()
    with trace("Autonomous Researcher - Trace", trace_id=trace_id):
        print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
        yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
        
        queue = asyncio.Queue()
        hooks = GradioRunHooks(queue)

        # Run the agent with streaming hooks
        result_streaming = Runner.run_streamed(
            AgenticResearchManager().research_agent,
            f"Query: {query}",
            hooks=hooks
        )

        # Accumulate all events
        accumulated_output = ""

        # Stream events from the queue to Gradio
        while True:
            event = await queue.get()
            accumulated_output += event  # append new event
            yield accumulated_output
            if "Agent Finished" in event:
                break



with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")
    
    run_button.click(fn=run_query, inputs=query_textbox, outputs=report)
    query_textbox.submit(fn=run_query, inputs=query_textbox, outputs=report)

ui.launch(inbrowser=True)

