import uuid
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["RCS"]

Base = declarative_base()

class ClientSQL(Base):
    __tablename__ = 'clients'
    id_client = Column(String(36), primary_key=True)
    nom = Column(String(255), nullable=False)
    prenom = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    mot2passe = Column(String(255), nullable=False)
    last_update = Column(DateTime, default=func.now())

engine = create_engine('mysql+pymysql://root:@localhost/RCS')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def handle_sync_failure(uuid, filename="failed_syncs.txt"):
    with open(filename, "a") as file:
        file.write(uuid + "\n")

def synchronize_to_sql():
    clients = mongo_db.clients.find()

    for client in clients:
        client_sql = session.query(ClientSQL).filter_by(id_client=client["_id"]).first()

        if client_sql is None:
            client_sql = ClientSQL(
                id_client=client["_id"],
                nom=client["nom"],
                prenom=client["prenom"],
                email=client["email"],
                mot2passe=client["mot2pass"]
            )
            session.add(client_sql)
        else:
            client_sql.nom = client["nom"]
            client_sql.prenom = client["prenom"]
            client_sql.email = client["email"]
            client_sql.mot2passe = client["mot2pass"]
            client_sql.last_update = datetime.now()

    session.commit()

def synchronize_to_mongo():
    clients = session.query(ClientSQL).all()

    for client in clients:
        client_mongo = mongo_db.clients.find_one({"_id": client.id_client})

        client_data = {
            "nom": client.nom,
            "prenom": client.prenom,
            "email": client.email,
            "mot2pass": client.mot2passe,
            "lastUpdate": client.last_update
        }

        if client_mongo is None:
            mongo_db.clients.insert_one({"_id": client.id_client, **client_data})
        else:
            mongo_db.clients.update_one({"_id": client.id_client}, {"$set": client_data})

def resolve_conflicts():
    clients = session.query(ClientSQL).all()
    
    for client in clients:
        client_mongo = mongo_db.clients.find_one({"_id": client.id_client})

        if client_mongo is None:
            client_mongo = {
                "_id": client.id_client,
                "nom": client.nom,
                "prenom": client.prenom,
                "email": client.email,
                "mot2pass": client.mot2passe,
                "lastUpdate": client.last_update
            }
            mongo_db.clients.insert_one(client_mongo)
        else:
            if client.last_update > client_mongo["lastUpdate"]:
                client_mongo["nom"] = client.nom
                client_mongo["prenom"] = client.prenom
                client_mongo["email"] = client.email
                client_mongo["mot2pass"] = client.mot2passe
                client_mongo["lastUpdate"] = client.last_update

                mongo_db.clients.update_one({"_id": client.id_client}, {"$set": client_mongo})
            else:
                client.id_client = client_mongo["_id"]
                client.nom = client_mongo["nom"]
                client.prenom = client_mongo["prenom"]
                client.email = client_mongo["email"]
                client.mot2passe = client_mongo["mot2pass"]
                client.last_update = client_mongo["lastUpdate"]
                
                session.commit()
    


def synchroniser_client():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation du client {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des clients:", e)
        

