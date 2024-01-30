import json
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['RCS']
clients = db['clients']
adresses = db['adresses']
categories = db['categories']
commandes = db['commandes']
produits = db['produits']


with open('client.json', 'r') as file:
    data = json.load(file)['clients']
print(data)
clients.insert_many(data)

with open('adresse.json', 'r') as file:
    data = json.load(file)['adresses']
adresses.insert_many(data)

with open('categorie.json', 'r') as file:
    data = json.load(file)['categories']
categories.insert_many(data)

with open('produit.json', 'r') as file:
    data = json.load(file)['produits']
produits.insert_many(data)

with open('commande.json', 'r') as file:
    data = json.load(file)['commandes']
commandes.insert_many(data)


print("Les données ont été insérées dans MongoDB.")
