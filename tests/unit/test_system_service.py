from src.mcp.services.system_service import get_system_status


def test_get_system_status():

    result = get_system_status()

    assert result["status"] == "healthy"

    assert "service" in result
    assert "version" in result