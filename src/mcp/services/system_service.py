from src.mcp.server.metadata import (
    SERVER_NAME,
    SERVER_VERSION,
)


def get_system_status() -> dict:
    """
    Returns the current system status.
    """

    return {
        "status": "healthy",
        "service": SERVER_NAME,
        "version": SERVER_VERSION,
    }