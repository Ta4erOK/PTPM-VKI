"""Юнит-тесты для класса Converter (ЛР4, срез знаний PTPM-VKI)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from converter import Converter


class TestUpperRange(unittest.TestCase):
    """x >= 100.7 -> 1000."""

    def test_lower_boundary(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_above_boundary(self):
        self.assertEqual(Converter.do(150.0), 1000)

    def test_large_value(self):
        self.assertEqual(Converter.do(9999.9), 1000)


class TestPositiveRange(unittest.TestCase):
    """0 < x < 100.7 -> int(x)."""

    def test_just_above_zero(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_small_fraction(self):
        self.assertEqual(Converter.do(0.9), 0)

    def test_typical_value(self):
        self.assertEqual(Converter.do(65.7), 65)

    def test_upper_boundary_minus_step(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_fraction_is_truncated(self):
        self.assertEqual(Converter.do(42.9), 42)


class TestZero(unittest.TestCase):
    """x == 0.0 -> ValueError."""

    def test_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_zero_raises(self):
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    def test_exception_has_message(self):
        with self.assertRaises(ValueError) as ctx:
            Converter.do(0.0)
        self.assertTrue(str(ctx.exception))


class TestNegativeRange(unittest.TestCase):
    """-30.4 <= x < 0 -> int(x) - 5."""

    def test_just_below_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_truncation_toward_zero(self):
        self.assertEqual(Converter.do(-0.9), -5)

    def test_typical_value(self):
        self.assertEqual(Converter.do(-15.5), -20)

    def test_lower_boundary(self):
        self.assertEqual(Converter.do(-30.4), -35)


class TestBottomRange(unittest.TestCase):
    """x <= -30.5 -> -2000."""

    def test_upper_boundary(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_value_from_task_example(self):
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_very_small_value(self):
        self.assertEqual(Converter.do(-1000.0), -2000)


class TestContract(unittest.TestCase):
    """Общие требования к контракту метода."""

    def test_returns_int(self):
        for value in (100.7, 65.7, 0.1, -0.1, -30.4, -30.5):
            with self.subTest(value=value):
                self.assertIsInstance(Converter.do(value), int)

    def test_callable_without_instance(self):
        # статический метод вызывается прямо от класса
        self.assertEqual(Converter.do(10.5), 10)

    def test_all_range_boundaries(self):
        cases = {
            100.7: 1000,
            100.6: 100,
            1.0: 1,
            0.1: 0,
            -0.1: -5,
            -30.4: -35,
            -30.5: -2000,
        }
        for x, expected in cases.items():
            with self.subTest(x=x):
                self.assertEqual(Converter.do(x), expected)


if __name__ == "__main__":
    unittest.main()
