import ast
import operator


class CalculatorTool:
	max_expression_length = 100
	max_nodes = 30
	max_abs_value = 10**12
	max_exponent = 12
	_ops = {
		ast.Add: operator.add,
		ast.Sub: operator.sub,
		ast.Mult: operator.mul,
		ast.Div: operator.truediv,
		ast.Mod: operator.mod,
		ast.Pow: operator.pow,
		ast.USub: operator.neg,
		ast.UAdd: operator.pos,
	}

	def _eval_node(self, node):
		if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
			return node.value

		if isinstance(node, ast.BinOp) and type(node.op) in self._ops:
			left = self._eval_node(node.left)
			right = self._eval_node(node.right)
			if isinstance(node.op, ast.Pow) and abs(right) > self.max_exponent:
				raise ValueError("Exponent is too large")
			result = self._ops[type(node.op)](left, right)
			if abs(result) > self.max_abs_value:
				raise ValueError("Result is too large")
			return result

		if isinstance(node, ast.UnaryOp) and type(node.op) in self._ops:
			value = self._eval_node(node.operand)
			return self._ops[type(node.op)](value)

		raise ValueError("Unsupported expression")

	def calculate(self, expression: str):
		try:
			if not expression or len(expression) > self.max_expression_length:
				raise ValueError("Expression is empty or too long")
			parsed = ast.parse(expression, mode="eval")
			if sum(1 for _ in ast.walk(parsed)) > self.max_nodes:
				raise ValueError("Expression is too complex")
			result = self._eval_node(parsed.body)
			return {
				"success": True,
				"result": result,
			}
		except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
			return {
				"success": False,
				"error": str(exc),
			}


calculator = CalculatorTool()