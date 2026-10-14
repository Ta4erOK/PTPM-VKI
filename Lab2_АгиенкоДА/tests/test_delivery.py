"""
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

    def test_distance_above_5000_returns_error(self):
        result, date = calculate_delivery_cost(2.0, 5001, "обычный")
        self.assertEqual((result, date), (-1, "0000-00-00"))

    def test_unknown_package_type_returns_error(self):
        result, date = calculate_delivery_cost(2.0, 100, "неопознанный")
        self.assertEqual((result, date), (-1, "0000-00-00"))


class TestDeliveryCostCommon(unittest.TestCase):
    def test_regular_small_weight_cost(self):
        result, _ = calculate_delivery_cost(2.0, 100, "обычный")
        self.assertEqual(result, 200 + 5 * 100)  # 700

    def test_weight_between_5_and_20_applies_12(self):
        result, _ = calculate_delivery_cost(10.0, 100, "обычный")
        self.assertEqual(result, 700 * 1.2)  # 840

    def test_fragile_adds_surcharge(self):
        result, _ = calculate_delivery_cost(2.0, 100, "хрупкий")
        self.assertEqual(result, 700 + 300)


class TestDeliveryDateCommon(unittest.TestCase):
    def test_short_distance_delivery_in_one_day(self):
        _, date = calculate_delivery_cost(2.0, 100, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_distance_1000_delivery_in_two_days(self):
        _, date = calculate_delivery_cost(2.0, 1000, "обычный")
        self.assertEqual(date, "2026-09-05")


class TestDeliveryExpress(unittest.TestCase):

    def test_express_is_more_expensive_than_regular(self):
        """Экспресс — ускоренная услуга, логично стоит дороже обычной."""
        regular_cost, _ = calculate_delivery_cost(2.0, 100, "обычный")
        express_cost, _ = calculate_delivery_cost(2.0, 100, "обычный", is_express=True)
        self.assertGreater(express_cost, regular_cost)

    def test_express_on_short_distance_cannot_be_same_day(self):
        """Даже экспресс не может доставить за 0 дней (дистанция >= 1 км)."""
        _, date = calculate_delivery_cost(2.0, 1, "обычный", is_express=True)
        self.assertGreaterEqual(date, "2026-09-04")


if __name__ == "__main__":
    unittest.main()