from src.mcp.services.calculator_service import add_numbers


def test_add_numbers():
    result = add_numbers(10, 20)

    assert result == {
        "result": 30
    }


def test_add_numbers_with_negative_values():
    result = add_numbers(-10, 5)

    assert result == {
        "result": -5
    }


def test_add_numbers_with_zero():
    result = add_numbers(0, 0)

    assert result == {
        "result": 0
    }