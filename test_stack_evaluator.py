"""Unit tests for stack_evaluator.py. Run with:  python -m unittest -v"""

import os
import tempfile
import unittest

from stack_evaluator import (ExpressionError, Stack, evaluate, format_result,
                             process_file)


class StackTests(unittest.TestCase):
    def test_push_pop_order_is_lifo(self):
        s = Stack()
        for n in (1, 2, 3):
            s.push(n)
        self.assertEqual([s.pop(), s.pop(), s.pop()], [3, 2, 1])

    def test_peek_does_not_remove(self):
        s = Stack()
        s.push("a")
        self.assertEqual(s.peek(), "a")
        self.assertEqual(s.size(), 1)

    def test_empty_stack_errors(self):
        s = Stack()
        self.assertTrue(s.is_empty())
        with self.assertRaises(IndexError):
            s.pop()
        with self.assertRaises(IndexError):
            s.peek()


class EvaluateTests(unittest.TestCase):
    def check(self, expression, expected):
        self.assertAlmostEqual(evaluate(expression), expected, places=9)

    def test_precedence(self):
        self.check("3 + 5 * 2", 13)
        self.check("10 - 6 / 3", 8)

    def test_parentheses(self):
        self.check("(8 / 4) + 7 * 2", 16)
        self.check("10 - (2 + 3) * 4", -10)
        self.check("2 * (3 + (4 - 1)) * 2", 24)

    def test_left_to_right(self):
        self.check("100 / 5 / 2", 10)
        self.check("10 - 4 - 3", 3)

    def test_unary_minus_and_decimals(self):
        self.check("-3 + 8", 5)
        self.check("4 * -2", -8)
        self.check("--5", 5)
        self.check("12.5 * 2 - 0.5", 24.5)

    def test_no_spaces_needed(self):
        self.check("2*(3+4)", 14)

    def test_bad_expressions(self):
        for bad in ("10 / (5 - 5)", "(2 + 3", "2 + 3)", "4 +", "* 5",
                    "8 $ 2", "2 3", "()", "", "1.2.3", "2 (3)"):
            with self.subTest(expression=bad):
                with self.assertRaises(ExpressionError):
                    evaluate(bad)

    def test_formatting(self):
        self.assertEqual(format_result(16.0), "16")
        self.assertEqual(format_result(3.5), "3.5")
        self.assertEqual(format_result(1 / 3), "0.333333")


class FileTests(unittest.TestCase):
    def test_round_trip_keeps_separators(self):
        with tempfile.TemporaryDirectory() as folder:
            src = os.path.join(folder, "in.txt")
            dst = os.path.join(folder, "out.txt")
            with open(src, "w") as f:
                f.write("1 + 1\n-----\n\n2 * 3\n-----\n5 / 0\n")
            process_file(src, dst)
            with open(dst) as f:
                self.assertEqual(f.read().splitlines(),
                                 ["2", "-----", "6", "-----",
                                  "Error: division by zero"])


if __name__ == "__main__":
    unittest.main()
