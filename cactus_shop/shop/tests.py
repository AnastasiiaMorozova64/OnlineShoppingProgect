# Create your tests here.
import pytest
from django.urls import reverse
from .models import Category, Product 
from django.db import models
from decimal import Decimal
from datetime import datetime

@pytest.fixture
def category(db):
    """Фікстура для створення категорії"""
    return Category.objects.create(name="Test Category", slug="test-category")

@pytest.fixture
def product(db, category):
    """Фікстура для створення продукту"""
    return Product.objects.create(
        category=category,
        name="Test Product",
        slug="test-product",
        price=Decimal("19.99"),
        stock=10,
        available=True,
        description="Test description"
    )

def test_category_str(category):
    """Тест строкового представлення категорії"""
    assert str(category) == "Test Category"

def test_category_get_absolute_url(category):
    """Тест генерації абсолютного URL для категорії"""
    expected_url = reverse('shop:product_list_by_category', args=['test-category'])
    assert category.get_absolute_url() == expected_url

def test_category_meta_ordering(category):
    """Тест сортування категорій за ім'ям"""
    category2 = Category.objects.create(name="Another Category", slug="another-category")
    categories = Category.objects.all()
    assert list(categories) == [category2, category]  # 'Another Category' йде першим за алфавітом

def test_category_meta_verbose_names():
    """Тест мета-опцій verbose_name та verbose_name_plural"""
    assert Category._meta.verbose_name == 'Category'
    assert Category._meta.verbose_name_plural == 'Categories'

def test_category_slug_unique(db):
    """Тест унікальності slug для категорії"""
    Category.objects.create(name="First Category", slug="unique-slug")
    with pytest.raises(Exception):  # IntegrityError для дубльованого slug
        Category.objects.create(name="Second Category", slug="unique-slug")

def test_product_str(product):
    """Тест строкового представлення продукту"""
    assert str(product) == "Test Product"

def test_product_get_absolute_url(product):
    """Тест генерації абсолютного URL для продукту"""
    expected_url = reverse('shop:product_detail', args=[product.id, 'test-product'])
    assert product.get_absolute_url() == expected_url

def test_product_category_relationship(category, product):
    """Тест зв'язку продукту з категорією"""
    assert product.category == category
    assert category.products.count() == 1
    assert category.products.first() == product

def test_product_meta_indexes():
    """Тест наявності індексу для полів id та slug"""
    indexes = Product._meta.indexes
    assert any(index.fields == ['id', 'slug'] for index in indexes)

def test_product_auto_timestamps(product):
    """Тест автоматичного заповнення полів created та updated"""
    assert isinstance(product.created, datetime)
    assert isinstance(product.updated, datetime)

def test_product_default_values(product):
    """Тест значень за замовчуванням для продукту"""
    assert product.available is True
    assert product.description == "Test description"
    assert product.stock == 10
    assert product.price == Decimal("19.99")

def test_product_image_field():
    """Тест поля image для продукту"""
    assert isinstance(Product._meta.get_field('image'), models.ImageField)
    assert Product._meta.get_field('image').upload_to == 'products/%Y/%m/%d'
    assert Product._meta.get_field('image').blank is True