from tools.calculator import CalculatorTool


def test_calculator_rejects_large_exponent():
    result = CalculatorTool().calculate("2 ** 100")

    assert result["success"] is False
    assert result["error"] == "Exponent is too large"


def test_calculator_rejects_division_by_zero():
    result = CalculatorTool().calculate("5 / 0")

    assert result["success"] is False
    assert "zero" in result["error"].lower()