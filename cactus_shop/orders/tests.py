import pytest
import time
from django.core.exceptions import ValidationError
from .models import Order, OrderItem, Product
from shop.models import Category
from decimal import Decimal
from datetime import datetime

# Фікстура для створення тестової категорії
@pytest.fixture
def category():
    return Category.objects.create(name="Тестова категорія")

# Фікстура для створення тестового продукту
@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Тестовий продукт",
        slug="testoviy-produkt",
        price=Decimal("10.00"),
        description="Тестовий опис",
        stock=10,
        available=True,
        category=category 
    )

# Фікстура для створення тестового замовлення
@pytest.fixture
def order():
    return Order.objects.create(
        first_name="Джон",
        last_name="Доу",
        email="john.doe@example.com",
        address="вул. Тестова, 123",
        postal_code="12345",
        city="Тестове місто",
        paid=False
    )

# Фікстура для створення тестового елемента замовлення
@pytest.fixture
def order_item(order, product):
    return OrderItem.objects.create(
        order=order,
        product=product,
        price=Decimal("10.00"),
        quantity=2
    )

@pytest.mark.django_db
class TestOrderModel:
    """Тест створення замовлення"""
    def test_order_creation(self, order):
        assert order.first_name == "Джон"
        assert order.last_name == "Доу"
        assert order.email == "john.doe@example.com"
        assert order.address == "вул. Тестова, 123"
        assert order.postal_code == "12345"
        assert order.city == "Тестове місто"
        assert order.paid is False
        assert isinstance(order.created, datetime)
        assert isinstance(order.updated, datetime)
        assert str(order) == f"Order {order.id}"

    """Тест валідації максимальної довжини полів замовлення"""
    def test_order_field_max_length(self):
        order = Order(
            first_name="A" * 51,  # Перевищує max_length=50
            last_name="Доу",
            email="test@example.com",
            address="вул. Тестова, 123",
            postal_code="12345",
            city="Тестове місто"
        )
        with pytest.raises(ValidationError):
            order.full_clean()

    """Тест валідації формату email у замовленні"""
    def test_order_email_validation(self):
        order = Order(
            first_name="Джон",
            last_name="Доу",
            email="invalid-email",  # Некоректний формат email
            address="вул. Тестова, 123",
            postal_code="12345",
            city="Тестове місто"
        )
        with pytest.raises(ValidationError):
            order.full_clean()

    """Тест сортування замовлень за датою створення"""
    def test_order_ordering(self, order):
        time.sleep(0.1)  # Додаємо затримку для забезпечення різних міток часу
        order2 = Order.objects.create(
            first_name="Джейн",
            last_name="Доу",
            email="jane.doe@example.com",
            address="вул. Тестова, 456",
            postal_code="67890",
            city="Тестове місто"
        )
        orders = Order.objects.all()
        assert orders[0] == order2, f"Очікувалося, що нове замовлення (id={order2.id}, created={order2.created}) буде першим, але отримали (id={orders[0].id}, created={orders[0].created})"
        assert orders[1] == order, f"Очікувалося, що старе замовлення (id={order.id}, created={order.created}) буде другим, але отримали (id={orders[1].id}, created={orders[1].created})"

    """Тест обчислення загальної вартості замовлення"""
    def test_get_total_cost(self, order, order_item):
        total_cost = order.get_total_cost()
        assert total_cost == Decimal("20.00")  # 2 товари * 10.00

    """Тест обчислення загальної вартості порожнього замовлення"""
    def test_get_total_cost_empty_order(self, order):
        assert order.get_total_cost() == Decimal("0.00")

@pytest.mark.django_db
class TestOrderItemModel:
    """Тест створення елемента замовлення"""
    def test_order_item_creation(self, order_item, order, product):
        assert order_item.order == order
        assert order_item.product == product
        assert order_item.price == Decimal("10.00")
        assert order_item.quantity == 2
        assert str(order_item) == str(order_item.id)

    """Тест обчислення вартості елемента замовлення"""
    def test_order_item_get_cost(self, order_item):
        assert order_item.get_cost() == Decimal("20.00")  # 10.00 * 2

    """Тест валідації від’ємної кількості в елементі замовлення"""
    def test_order_item_negative_quantity(self, order, product):
        order_item = OrderItem(
            order=order,
            product=product,
            price=Decimal("10.00"),
            quantity=-1
        )
        with pytest.raises(ValidationError):
            order_item.full_clean()

    """Тест валідації точності ціни в елементі замовлення"""
    def test_order_item_price_precision(self, order, product):
        order_item = OrderItem(
            order=order,
            product=product,
            price=Decimal("10.123"),  # Перевищує decimal_places=2
            quantity=1
        )
        with pytest.raises(ValidationError):
            order_item.full_clean()

    """Тест каскадного видалення елемента замовлення"""
    def test_order_item_cascade_delete(self, order, order_item):
        order_id = order.id
        order.delete()
        assert not OrderItem.objects.filter(id=order_item.id).exists()