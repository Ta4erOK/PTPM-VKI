"""Тесты для учебного модуля расчёта доставки (delivery_service.py).

Бизнес-логика восстановлена по исходному коду и здравому смыслу:
1. Физические границы: вес 0.1..50 кг, дистанция 1..5000 км (иначе -1).
2. Допустимые типы: обычный, хрупкий, опасный (иначе -1).
3. Стоимость = 200 руб + 5 руб за км.
4. Вес >5 и <20 кг -> *1.2; вес >=20 кг -> *1.5.
5. Хрупкий +300 руб, опасный +1000 руб.
6. Экспресс — ускоренная доставка, должна стоить ДОРОЖЕ обычной.
7. Срок: минимум 1 день; экспресс быстрее, но тоже минимум 1 день.
Отправка фиксирована: 2026-09-03.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from delivery_service import calculate_delivery_cost


class TestDeliveryValidation(unittest.TestCase):
    def test_weight_below_lower_bound_returns_error(self):
        result, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_weight_above_upper_bound_returns_error(self):
        result, date = calculate_delivery_cost(51.0, 100, "обычный")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_distance_below_one_returns_error(self):
        result, date = calculate_delivery_cost(2.0, 0, "обычный")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_distance_above_5000_returns_error(self):
        result, date = calculate_delivery_cost(2.0, 5001, "обычный")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_unknown_package_type_returns_error(self):
        result, date = calculate_delivery_cost(2.0, 100, "неопознанный")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_empty_package_type_returns_error(self):
        result, date = calculate_delivery_cost(2.0, 100, "")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_boundary_weight_010_accepted(self):
        result, date = calculate_delivery_cost(0.1, 100, "обычный")
        self.assertNotEqual(result, -1)

    def test_boundary_weight_500_accepted(self):
        result, date = calculate_delivery_cost(50.0, 100, "обычный")
        self.assertNotEqual(result, -1)

    def test_boundary_distance_1_accepted(self):
        result, date = calculate_delivery_cost(2.0, 1, "обычный")
        self.assertEqual(result, 205)

    def test_boundary_distance_5000_accepted(self):
        result, date = calculate_delivery_cost(2.0, 5000, "обычный")
        self.assertEqual(result, 200 + 5 * 5000)


class TestDeliveryCostCommon(unittest.TestCase):
    def test_regular_small_weight_cost(self):
        result, _ = calculate_delivery_cost(2.0, 100, "обычный")
        self.assertEqual(result, 200 + 5 * 100)  # 700

    def test_weight_5_kg_no_coefficient(self):
        result, _ = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(result, 700)

    def test_weight_between_5_and_20_applies_12(self):
        result, _ = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(result, 700 * 1.2)  # 840

    def test_weight_20_kg_applies_15(self):
        result, _ = calculate_delivery_cost(20.0, 100, "обычный")
        self.assertEqual(result, 700 * 1.5)  # 1050

    def test_weight_25_kg_applies_15(self):
        result, _ = calculate_delivery_cost(25.0, 100, "обычный")
        self.assertEqual(result, 700 * 1.5)

    def test_fragile_adds_surcharge(self):
        result, _ = calculate_delivery_cost(2.0, 100, "хрупкий")
        self.assertEqual(result, 700 + 300)

    def test_dangerous_adds_surcharge(self):
        result, _ = calculate_delivery_cost(2.0, 100, "опасный")
        self.assertEqual(result, 700 + 1000)


class TestDeliveryDateCommon(unittest.TestCase):
    def test_short_distance_delivery_in_one_day(self):
        _, date = calculate_delivery_cost(2.0, 100, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_distance_500_delivery_in_one_day(self):
        _, date = calculate_delivery_cost(2.0, 500, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_distance_1000_delivery_in_two_days(self):
        _, date = calculate_delivery_cost(2.0, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")

    def test_distance_1500_delivery_in_three_days(self):
        _, date = calculate_delivery_cost(2.0, 1500, "обычный")
        self.assertEqual(date, "2026-09-06")


class TestDeliveryExpress(unittest.TestCase):
    """Ожидаемое поведение экспресс-доставки (тут должны найтись баги)."""

    def test_express_is_more_expensive_than_regular(self):
        """Экспресс — ускоренная услуга, логично стоит дороже обычной."""
        regular_cost, _ = calculate_delivery_cost(2.0, 100, "обычный")
        express_cost, _ = calculate_delivery_cost(2.0, 100, "обычный", is_express=True)
        self.assertGreater(express_cost, regular_cost)

    def test_express_on_short_distance_cannot_be_same_day(self):
        """Даже экспресс не может доставить за 0 дней (дистанция >= 1 км)."""
        _, date = calculate_delivery_cost(2.0, 1, "обычный", is_express=True)
        self.assertGreaterEqual(date, "2026-09-04")

    def test_express_delivers_faster_than_regular(self):
        """Экспресс должен быть быстрее обычной доставки на той же дистанции."""
        regular_cost, regular_date = calculate_delivery_cost(2.0, 1000, "обычный")
        express_cost, express_date = calculate_delivery_cost(2.0, 1000, "обычный", is_express=True)
        self.assertLess(express_date, regular_date)

    def test_express_on_1000km_delivery_in_one_day(self):
        """1000 км обычным — 2 дня, экспрессом — 1 день (не 0)."""
        _, date = calculate_delivery_cost(2.0, 1000, "обычный", is_express=True)
        self.assertEqual(date, "2026-09-04")

    def test_express_on_2000km_delivery_in_two_days(self):
        """2000 км обычным — 4 дня, экспрессом — 2 дня."""
        _, date = calculate_delivery_cost(2.0, 2000, "обычный", is_express=True)
        self.assertEqual(date, "2026-09-05")


if __name__ == "__main__":
    unittest.main()