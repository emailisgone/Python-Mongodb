from flask import (Flask, request, jsonify, abort)
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.flaskDatabase
clientsCollection = db.clients
productsCollection = db.products

clientCounter = 0

@app.route('/clients', methods=['PUT'])
def registerClient():
    global clientCounter
    
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data:
        return 'Invalid input, missing name or email', 400
    
    existingClient = clientsCollection.find_one({'id': data['id']})
    if existingClient:
        return 'Client with this id already exists', 400

    newClient = {
        'id': data['id'],        
        'name': data['name'],
        'email': data['email'],
        'intId': clientCounter  
    }

    clientsCollection.insert_one(newClient)

    clientCounter += 1

    return jsonify({'id': newClient['intId']}), 201

@app.route('/clients/<clientId>', methods=['GET'])
def getClient(clientId):
    client = clientsCollection.find_one({'id': clientId})

    if not client:
        return 'Client not found', 404

    clientData = {
        'id': client['intId'],
        'name': client['name'],
        'email': client['email']
    }

    return jsonify(clientData), 200

@app.route('/clients/<clientId>', methods=['DELETE'])
def deleteClient(clientId):
    client = clientsCollection.delete_one({'id': clientId})

    if client.deleted_count == 0:
        return 'Client not found', 404

    return 'Client deleted', 204

@app.route('/products', methods=['PUT'])
def registerProduct():
    data = request.get_json()

    if not data or 'id' not in data or 'name' not in data or 'price' not in data or data['price']<0:
        return 'Invalid input, missing name or price', 400

    existingProduct = productsCollection.find_one({'id': data['id']})
    if existingProduct:
        return 'Product with this id already exists', 400

    newProduct = {
        'id': data['id'],
        'name': data['name'],
        'category': data['category'],
        'description': data['description'],
        'price': data['price']
    }
    productsCollection.insert_one(newProduct)

    return jsonify({'id': newProduct['id']}), 201

@app.route('/products', methods=['GET'])
def listProducts():
    try:
        data = request.get_json()
    except Exception as e:
        data = None

    if not data or 'category' not in data:
        productList = list(productsCollection.find({}, {'_id': 0}))
        return jsonify(productList), 200

    productList = list(productsCollection.find({'category': data['category']}, {'_id': 0}))
    return jsonify(productList), 200

@app.route('/products/<productId>', methods=['GET'])
def getProductDetails(productId):
    product = productsCollection.find_one({'id': productId}, {'_id': 0})

    if not product:
        return 'Product not found', 404

    return jsonify(product), 200

@app.route('/products/<productId>', methods=['DELETE'])
def deleteProduct(productId):
    product = productsCollection.find_one({'id': productId}, {'_id': 0})

    if not product:
        return 'Product not found', 404

    productsCollection.delete_one({'id': productId})

    return 'Product deleted', 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)