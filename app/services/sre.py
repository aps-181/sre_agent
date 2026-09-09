import sys

def fetch_service_logs(service_name: str) -> str:
    print(f"[Server] Tool called: fetch_service_logs for '{service_name}'", file=sys.stderr)
    mock_logs = {
        "payment-gateway": "[ERROR] 10:05 UTC - DB Connection pool exhausted. Timeout executing query.",
        "kafka-consumer": "[WARN] 10:12 UTC - Consumer lag exceeded 1000 messages on topic 'orders'."
    }
    return mock_logs.get(service_name, f"No logs found for {service_name}. Service might be healthy.")

def fetch_db_metrics(database_name: str = "payments_db") -> str:
    print(f"[Server] Tool called: fetch_db_metrics for '{database_name}'", file=sys.stderr)
    return f"DB '{database_name}': 100% connection pool utilization, CPU 95%"