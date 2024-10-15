from flask import (Flask, request, jsonify, abort)
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.flaskDatabase
clientsCollection = db.clients

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)