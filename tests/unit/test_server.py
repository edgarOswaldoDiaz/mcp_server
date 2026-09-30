from src.mcp.server.main import create_server


def test_create_server():

    server = create_server(use_auth=False)

    assert server is not None