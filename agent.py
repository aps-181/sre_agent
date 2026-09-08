import asyncio
import os
import json
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# 1. Define the strict JSON output schema
class InvestigationResult(BaseModel):
    summary: str
    evidence: list[str]
    root_cause: str
    recommended_actions: list[str]

# 2. Configure Pydantic AI model for Ollama
local_model = OllamaModel(
    model_name='qwen3:8b',
    provider=OllamaProvider(base_url='http://localhost:11434/v1')
)

# 3. Initialize the Agent
agent = Agent(
    model=local_model,
    output_type=InvestigationResult,
    system_prompt=(
        "You are an expert Site Reliability Engineer (SRE). "
        "Investigate the provided issue using the available tools. "
        "Gather evidence, determine the root cause, and return a structured JSON report."
    )
)

async def main():
    issue = "The payment-gateway is down. Please investigate."
    print(f"Investigating: {issue}...\n")

    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV", "")
    }

    # 4. Define connection parameters for the local MCP Server
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        env=safe_env
    )
    
    # 5. Connect and initialize session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 6. Discover tools from the server
            mcp_tools = await session.list_tools()
            tool_descriptions = "\n".join(
                [f"- {t.name}: {t.description}" for t in mcp_tools.tools]
            )
            
            # 7. Register local tool to bridge execution to MCP safely
            @agent.tool_plain
            async def execute_mcp_tool(tool_name: str, arguments: str = "{}") -> str:
                """
                Call this tool to execute external SRE tools. 
                Pass the 'tool_name' and a JSON string of 'arguments'.
                """
                print(f"  [Agent called tool] -> {tool_name}({arguments})")
                
                # Safely handle empty strings or malformed JSON
                if not arguments or arguments.strip() in ("", "None"):
                    args_dict = {}
                else:
                    try:
                        args_dict = json.loads(arguments)
                    except json.JSONDecodeError:
                        args_dict = {}

                result = await session.call_tool(tool_name, args_dict)
                return result.content[0].text
            
            prompt = (
                f"Issue: {issue}\n\n"
                f"You have access to the following external tools via 'execute_mcp_tool':\n"
                f"{tool_descriptions}\n\n"
                f"For example, to get logs, pass tool_name='get_service_logs' and arguments='{{\"service_name\": \"payment-gateway\"}}'."
            )
            
            # 8. Run agent execution loop
            result = await agent.run(prompt)
            
            print("\n--- RCA REPORT (Structured Output) ---")
            print(result.output.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())