import math
import requests
import pytest

HOST = "localhost"
PORT = 5000

@pytest.fixture(scope='module', autouse=True)
def setup_module():
    try:
        requests.post(f'http://{HOST}:{PORT}/cleanup')
    except Exception:
        print("Warning: cleanup failed")

def test_registering_unregistering_clients():
    client_id = register_new_client("Alice", "alice@test.com")

    client = get_client(client_id)
    assert client['name'] == "Alice"
    assert client['email'] == "alice@test.com"

    delete_client(client_id)

    get_client_response = get_client_raw(client_id)
    assert get_client_response.status_code == 404

def test_registering_products_with_missing_data():
    register_product_no_price()

def test_registering_products():
    product_id = register_product("Apple", "Fruit", 1.2)

    product = get_product(product_id)
    assert product['name'] == "Apple"
    assert product['category'] == "Fruit"
    assert math.isclose(product['price'], 1.2)

    delete_product(product_id)

    get_product_response = get_product_raw(product_id)
    assert get_product_response.status_code == 404

def test_querying_products():
    product_id = register_product("Apple", "Fruit", 1.2)
    product2_id = register_product("Banana", "Fruit", 0.8)
    product3_id = register_product("Orange", "Fruit", 1.0)
    product4_id = register_product("Tomato", "Berry", 2.0)

    products = get_products_by_category("Fruit")
    assert len(products) == 3
    assert products[0]['name'] == "Apple"
    assert products[1]['name'] == "Banana"
    assert products[2]['name'] == "Orange"

    products = get_products_by_category("Berry")
    assert len(products) == 1
    assert products[0]['name'] == "Tomato"

    delete_product(product_id)
    delete_product(product2_id)
    delete_product(product3_id)
    delete_product(product4_id)

def test_placing_orders_and_statistics():
    client_id = register_new_client("John Smith", "john@smith.com")
    client2_id = register_new_client("Jane Doe", "john@doe.com")
    product_id = register_product("Banana", "Fruit", 0.8)
    product2_id = register_product("Orange", "Fruit", 1.0)
    product3_id = register_product("Tomato", "Berry", 2.0)

    place_order(client_id, product_id, 10)
    place_order(client_id, product2_id, 5)
    place_order_multiple_items(
        client_id, 
        [{'productId': product_id, 'quantity': 10}, {'productId': product2_id, 'quantity': 5}]
    )
    place_order_multiple_items(
        client_id, 
        [{'productId': product_id, 'quantity': 10}, {'productId': product2_id, 'quantity': 5}, {'productId': product3_id, 'quantity': 2}]
    )
    place_order(client2_id, product3_id, 4)
    place_order_multiple_items(
        client2_id, 
        [{'productId': product3_id, 'quantity': 1}, {'productId': product2_id, 'quantity': 1}, {'productId': product_id, 'quantity': 2}]
    )

    assert get_number_of_orders_placed() == 6
    assert math.isclose(get_total_order_value(), 10 * 0.8 + 5 * 1.0 + (10 * 0.8 + 5 * 1.0) + (10 * 0.8 + 5 * 1.0 + 2 * 2.0) + (4 * 2.0) + (1 * 2.0 + 1 * 1.0 + 2 * 0.8))

    top_products = get_top_products()

    assert len(top_products) == 3
    assert top_products[0]['name'] == "Banana"
    assert top_products[0]['quantity'] == 10 + 10 + 10 + 2

    assert top_products[1]['name'] == "Orange"
    assert top_products[1]['quantity'] == 5 + 5 + 5 + 1

    assert top_products[2]['name'] == "Tomato"
    assert top_products[2]['quantity'] == 2 + 4 + 1

    top_clients = get_top_clients()

    assert len(top_clients) == 2
    assert top_clients[0]['id'] == client_id
    assert top_clients[0]['name'] == "John Smith"
    assert top_clients[0]['totalOrders'] == 4

    assert top_clients[1]['id'] == client2_id
    assert top_clients[1]['name'] == "Jane Doe"
    assert top_clients[1]['totalOrders'] == 2

    delete_client(client_id)
    delete_client(client2_id)
    delete_product(product_id)
    delete_product(product2_id)
    delete_product(product3_id)


def register_new_client(name, email):
    response = requests.put(f'http://{HOST}:{PORT}/clients', json={'name': name, 'email': email})
    assert response.status_code == 201
    return response.json()['id']

def get_client_raw(id):
    response = requests.get(f'http://{HOST}:{PORT}/clients/{id}')
    return response

def get_client(id):
    response = get_client_raw(id)
    assert response.status_code == 200
    return response.json()

def delete_client(id):
    response = requests.delete(f'http://{HOST}:{PORT}/clients/{id}')
    assert response.status_code == 204

def register_product(name, category, price):
    response = requests.put(f'http://{HOST}:{PORT}/products', json={'name': name, 'category': category, 'price': price})
    assert response.status_code == 201
    return response.json()['id']

def register_product_no_price():
    response = requests.put(f'http://{HOST}:{PORT}/products', json={'name': 'Bogus', 'category': 'Bogus'})
    assert response.status_code == 400
    
def get_product_raw(id):
    response = requests.get(f'http://{HOST}:{PORT}/products/{id}')
    return response

def get_product(id):
    response = get_product_raw(id)
    assert response.status_code == 200
    return response.json()

def get_products_by_category(category):
    response = requests.get(f'http://{HOST}:{PORT}/products?category={category}')
    assert response.status_code == 200
    return response.json()

def delete_product(id):
    response = requests.delete(f'http://{HOST}:{PORT}/products/{id}')
    assert response.status_code == 204

def place_order(client_id, product_id, quantity):
    response = requests.put(f'http://{HOST}:{PORT}/orders', json={'clientId': client_id, 'items': [{'productId': product_id, 'quantity': quantity}]})
    assert response.status_code == 201
    return response.json()['id']

def place_order_multiple_items(client_id, items):
    response = requests.put(f'http://{HOST}:{PORT}/orders', json={'clientId': client_id, 'items': items})
    assert response.status_code == 201
    return response.json()['id']

def get_number_of_orders_placed():
    response = requests.get(f'http://{HOST}:{PORT}/statistics/orders/total')
    assert response.status_code == 200
    return response.json()['total']

def get_total_order_value():
    response = requests.get(f'http://{HOST}:{PORT}/statistics/orders/totalValue')
    assert response.status_code == 200
    return response.json()['totalValue']

def get_top_clients():
    response = requests.get(f'http://{HOST}:{PORT}/statistics/top/clients')
    assert response.status_code == 200
    return response.json()

def get_top_products():
    response = requests.get(f'http://{HOST}:{PORT}/statistics/top/products')
    assert response.status_code == 200
    return response.json()