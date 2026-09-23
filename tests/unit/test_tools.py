from src.mcp.server.main import create_server


def test_server_creation():

    server = create_server()

    assert server is not None

def test_add():

    assert 10 + 20 == 30