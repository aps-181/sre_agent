from fastmcp import FastMCP
from app.services.sre import fetch_service_logs, fetch_db_metrics

mcp = FastMCP("TriageTools")


@mcp.tool()
def get_service_logs(service_name: str) -> str:
    """Fetches recent logs for a specific service."""
    return fetch_service_logs(service_name)


@mcp.tool()
def query_db_metrics(database_name: str = "payments_db") -> str:
    """Fetches database connection and CPU metrics."""
    return fetch_db_metrics(database_name)


if __name__ == "__main__":
    mcp.run()
