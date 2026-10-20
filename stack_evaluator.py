"""
DCOMP320 Data Structures and Algorithm - Assignment 1: Stacks Implementation
Student : Mohamed Alie Kamara (BSEM 2102)

Reads mathematical expressions from input.txt, evaluates each one with a
stack-based algorithm, and writes the answers to output.txt. Separator lines
(a line made only of dashes, e.g. -----) are copied through untouched, so the
output file has exactly the same shape as the input file.

Usage:
    python stack_evaluator.py                      # input.txt -> output.txt
    python stack_evaluator.py in.txt out.txt       # custom file names
"""

import re
import sys


# --------------------------------------------------------------------------
# 1. The Stack
# --------------------------------------------------------------------------
class Stack:
    """A last-in, first-out (LIFO) stack built on top of a Python list.

    The end of the list is the top of the stack, so push and pop both work
    on the end and run in O(1) time.
    """

    def __init__(self):
        self._items = []

    def push(self, item):
        """Place an item on top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from an empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek at an empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items})"


# --------------------------------------------------------------------------
# 2. Expression evaluation
# --------------------------------------------------------------------------
class ExpressionError(Exception):
    """Raised when an expression is malformed or cannot be calculated."""


# Binary operators: higher number binds tighter. "neg" is unary minus and
# beats everything, so -2 * 3 is read as (-2) * 3.
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "neg": 3}
NUMBER_PATTERN = re.compile(r"\d+\.\d+|\d+|\.\d+")


def tokenize(expression):
    """Split an expression string into numbers, operators and parentheses."""
    tokens = []
    i = 0
    while i < len(expression):
        ch = expression[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            match = NUMBER_PATTERN.match(expression, i)
            if not match:
                raise ExpressionError(f"invalid number near position {i + 1}")
            text = match.group()
            tokens.append(float(text) if "." in text else int(text))
            i = match.end()
            # Catches things like 1.2.3, which would otherwise split silently.
            if i < len(expression) and expression[i] == ".":
                raise ExpressionError(f"invalid number near position {i + 1}")
        elif ch in "+-*/()":
            tokens.append(ch)
            i += 1
        else:
            raise ExpressionError(f"unexpected character '{ch}'")
    return tokens


def apply_operator(operator, operands):
    """Pop the needed operands, perform one operation, push the result."""
    if operator == "neg":
        operands.push(-operands.pop())
        return

    right = operands.pop()   # the second operand sits on top
    left = operands.pop()
    if operator == "+":
        operands.push(left + right)
    elif operator == "-":
        operands.push(left - right)
    elif operator == "*":
        operands.push(left * right)
    elif operator == "/":
        if right == 0:
            raise ExpressionError("division by zero")
        operands.push(left / right)


def evaluate(expression):
    """Evaluate an infix expression using two stacks (Dijkstra's approach).

    One stack holds numbers waiting to be used, the other holds operators
    and open brackets waiting for their turn. An operator is only applied
    once the next operator has lower or equal precedence, which is what
    enforces the precedence and left-to-right rules.
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ExpressionError("empty expression")

    operands = Stack()
    operators = Stack()
    expect_operand = True   # True when a number, '(' or unary '-' must come next

    for token in tokens:
        if isinstance(token, (int, float)):
            if not expect_operand:
                raise ExpressionError("missing operator between values")
            operands.push(token)
            expect_operand = False

        elif token == "(":
            if not expect_operand:
                raise ExpressionError("missing operator before '('")
            operators.push("(")

        elif token == ")":
            if expect_operand:
                raise ExpressionError("missing value before ')'")
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators.pop(), operands)
            if operators.is_empty():
                raise ExpressionError("unbalanced parentheses")
            operators.pop()  # discard the matching '('
            expect_operand = False

        else:  # + - * /
            if expect_operand:
                if token == "-":
                    operators.push("neg")      # unary minus
                elif token == "+":
                    pass                       # unary plus changes nothing
                else:
                    raise ExpressionError(f"operator '{token}' has no left value")
            else:
                while (not operators.is_empty()
                       and operators.peek() != "("
                       and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]):
                    apply_operator(operators.pop(), operands)
                operators.push(token)
                expect_operand = True

    if expect_operand:
        raise ExpressionError("expression ends with an operator")

    while not operators.is_empty():
        top = operators.pop()
        if top == "(":
            raise ExpressionError("unbalanced parentheses")
        apply_operator(top, operands)

    return operands.peek()


def format_result(value):
    """Print whole numbers without a trailing .0, trim long decimals."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


# --------------------------------------------------------------------------
# 3. File handling
# --------------------------------------------------------------------------
SEPARATOR = re.compile(r"^\s*-{3,}\s*$")


def process_file(input_path, output_path):
    """Evaluate every expression in input_path and write output_path.

    Separator lines are copied as they are. Blank lines are skipped. A bad
    expression produces an 'Error: ...' line instead of stopping the run.
    Returns the list of output lines.
    """
    results = []
    with open(input_path, "r", encoding="utf-8") as source:
        for raw_line in source:
            line = raw_line.strip()
            if not line:
                continue
            if SEPARATOR.match(line):
                results.append(line)
                continue
            try:
                results.append(format_result(evaluate(line)))
            except ExpressionError as problem:
                results.append(f"Error: {problem}")

    with open(output_path, "w", encoding="utf-8") as target:
        target.write("\n".join(results) + "\n")
    return results


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    try:
        lines = process_file(input_path, output_path)
    except FileNotFoundError:
        print(f"Could not find '{input_path}'. Put it in the same folder and try again.")
        sys.exit(1)
    count = sum(1 for line in lines if not SEPARATOR.match(line))
    print(f"Done. {count} result(s) written to {output_path}")


if __name__ == "__main__":
    main()
