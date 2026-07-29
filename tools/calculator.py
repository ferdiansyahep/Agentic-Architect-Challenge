import ast
import operator


class CalculatorTool:
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
			return self._ops[type(node.op)](left, right)

		if isinstance(node, ast.UnaryOp) and type(node.op) in self._ops:
			value = self._eval_node(node.operand)
			return self._ops[type(node.op)](value)

		raise ValueError("Unsupported expression")

	def calculate(self, expression: str):
		try:
			parsed = ast.parse(expression, mode="eval")
			result = self._eval_node(parsed.body)
			return {
				"success": True,
				"result": result,
			}
		except Exception as exc:
			return {
				"success": False,
				"error": str(exc),
			}


calculator = CalculatorTool()
