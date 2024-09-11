from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from ..main import app, get_db
from ..database import Product, ProductCreate

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    db = MagicMock(spec=Session)
    return db


def test_create_product(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session
    product_data = {
        "name": "Test Product",
        "price": 10.99,
        "category": "Test Category"
    }

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    response = client.post("/products/", json=product_data)

    assert response.status_code == 200

    product = response.json()
    assert product["name"] == product_data["name"]
    assert product["price"] == product_data["price"]
    assert product["category"] == product_data["category"]

    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


def test_read_categories(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_categories = [
        ('Electronics',),
        ('Furniture',),
        ('Clothing',)
    ]

    mock_query = MagicMock()
    mock_query.all.return_value = mock_categories
    mock_db_session.query.return_value = mock_query

    response = client.get("/categories/")

    assert response.status_code == 200

    categories = response.json()
    assert categories == ['Electronics', 'Furniture', 'Clothing']

    mock_db_session.query.assert_called_once()
    mock_query.all.assert_called_once()


def test_read_product(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

    product_id = 1
    product_data = {
        "id": product_id,
        "name": "Test Product",
        "price": 10.99,
        "category": "Test Category"
    }

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = Product(**product_data)
    mock_db_session.query.return_value = mock_query

    response = client.get(f"/products/{product_id}")

    assert response.status_code == 200

    product = response.json()
    assert product["id"] == product_id
    assert product["name"] == product_data["name"]
    assert product["price"] == product_data["price"]
    assert product["category"] == product_data["category"]

    mock_db_session.query.assert_called_once()
    mock_query.filter.assert_called_once()


def test_read_product_not_found(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db_session.query.return_value = mock_query

    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Product not found"}

    mock_db_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    mock_query.filter.return_value.first.assert_called_once()


def test_update_product(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

    product_id = 1
    existing_product = Product(id=product_id, name="Old Product", price=5.99, category="Old Category")

    updated_product_data = ProductCreate(
        name="Updated Product",
        price=10.99,
        category="Updated Category"
    )

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = existing_product
    mock_db_session.query.return_value = mock_query

    mock_db_session.commit.return_value = None

    response = client.put(f"/products/{product_id}", json=updated_product_data.dict())

    assert response.status_code == 200

    product = response.json()
    assert product["id"] == product_id
    assert product["name"] == updated_product_data.name
    assert product["price"] == updated_product_data.price
    assert product["category"] == updated_product_data.category

    mock_db_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_delete_product(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

    product_id = 1
    existing_product = Product(id=product_id, name="Test Product", price=10.99, category="Test Category")

    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = existing_product
    mock_db_session.query.return_value = mock_query

    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    response = client.delete(f"/products/{product_id}")

    assert response.status_code == 200

    assert response.json() == {"detail": "Product deleted"}

    mock_db_session.query.assert_called_once()
    mock_query.filter.assert_called_once()
    mock_query.filter.return_value.first.assert_called_once()
    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_read_products(mock_db_session):
    app.dependency_overrides[get_db] = lambda: mock_db_session

    products = [
        {"id": 1, "name": "Milk", "price": 10.99, "category": "Eat"},
        {"id": 2, "name": "Milk", "price": 20.99, "category": "Eat"},
        {"id": 3, "name": "Milk", "price": 30.99, "category": "Eat"},
    ]

    mock_query = MagicMock()
    mock_query.all.return_value = products
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_db_session.query.return_value = mock_query

    response = client.get("/products/")

    assert response.status_code == 200

    response_products = response.json()

    assert len(response_products) == 3
    assert response_products[2]["price"] == 30.99
    assert response_products[1]["price"] == 20.99
    assert response_products[0]["price"] == 10.99

    mock_db_session.query.assert_called_once()
    mock_query.filter.assert_not_called()
    mock_query.order_by.assert_called_once()
