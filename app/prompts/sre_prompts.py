SRE_SYSTEM_PROMPT = (
    "You are an expert Site Reliability Engineer (SRE). "
    "Investigate the provided issue using the available tools. "
    "Gather evidence, determine the root cause, and return a structured JSON report."
)


def build_investigation_prompt(issue: str, tool_descriptions: str) -> str:
    return (
        f"Issue: {issue}\n\n"
        f"You have access to the following external tools via 'execute_mcp_tool':\n"
        f"{tool_descriptions}\n\n"
        f"For example, to get logs, pass tool_name='get_service_logs' and arguments='{{\"service_name\": \"payment-gateway\"}}'."
    )
