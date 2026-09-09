import asyncio
import os
import json
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

from app.config import settings
from app.schemas.investigation import InvestigationResult
from app.prompts.sre_prompts import SRE_SYSTEM_PROMPT, build_investigation_prompt

local_model = OllamaModel(
    model_name=settings.MODEL_NAME,
    provider=OllamaProvider(base_url=settings.OLLAMA_BASE_URL)
)

agent = Agent(
    model=local_model,
    output_type=InvestigationResult,
    system_prompt=SRE_SYSTEM_PROMPT
)

async def main():
    issue = "The payment-gateway is down. Please investigate."
    print(f"Investigating: {issue}...\n")

    safe_env = {
        "PATH": os.environ.get("PATH", ""),
        "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV", "")
    }

    # Execute module directly to preserve package import resolution
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.mcp.server"],
        env=safe_env
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            mcp_tools = await session.list_tools()
            tool_descriptions_list = []

            for t in mcp_tools.tools:
                schema_props = t.inputSchema.get("properties", {}) if isinstance(t.inputSchema, dict) else {}
                params = [f"{p_name}: {p_info.get('type', 'str')}" for p_name, p_info in schema_props.items()]
                params_str = f"({', '.join(params)})" if params else "()"
                tool_descriptions_list.append(f"- {t.name}{params_str}: {t.description}")

            tool_descriptions = "\n".join(tool_descriptions_list)
            
            @agent.tool_plain
            async def execute_mcp_tool(tool_name: str, arguments: str = "{}") -> str:
                """Call this tool to execute external SRE tools."""
                print(f"  [Agent called tool] -> {tool_name}({arguments})")
                
                if not arguments or arguments.strip() in ("", "None"):
                    args_dict = {}
                else:
                    try:
                        args_dict = json.loads(arguments)
                    except json.JSONDecodeError:
                        args_dict = {}

                result = await session.call_tool(tool_name, args_dict)
                return result.content[0].text
            
            prompt = build_investigation_prompt(issue, tool_descriptions)
            result = await agent.run(prompt)
            
            print("\n--- RCA REPORT (Structured Output) ---")
            print(result.output.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())