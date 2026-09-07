# mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TriageTools")

# 2. Expose tools using the @mcp.tool() decorator
@mcp.tool()
def get_service_logs(service_name: str) -> str:
    """
    Fetches recent logs for a specific service.
    Use this to investigate application errors or crashes.
    """
    print(f"[Server] Tool called: get_service_logs for '{service_name}'")
    
    # Mock data to simulate real system logs
    mock_logs = {
        "payment-gateway": "[ERROR] 10:05 UTC - DB Connection pool exhausted. Timeout executing query.",
        "kafka-consumer": "[WARN] 10:12 UTC - Consumer lag exceeded 1000 messages on topic 'orders'."
    }
    return mock_logs.get(service_name, f"No logs found for {service_name}. Service might be healthy.")

@mcp.tool()
def query_db_metrics(database_name: str) -> str:
    """
    Fetches database connection and CPU metrics.
    Use this to determine if a database is overloaded.
    """
    print(f"[Server] Tool called: query_db_metrics for '{database_name}'")
    
    # Mock data to simulate a database state
    return f"DB '{database_name}': 100% connection pool utilization, CPU 95%"

if __name__ == "__main__":
    # 3. Run the server using Standard I/O (stdio)
    # This allows our agent process to talk to it securely via standard input/output.
    print("Starting MCP Server: TriageTools...")
    mcp.run()