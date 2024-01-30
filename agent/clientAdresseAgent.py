import uuid
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func, ForeignKey
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
    
class AdressesSQL(Base):
    __tablename__ = "adresses"
    id_adresse = Column(String(36), primary_key=True)
    door = Column(String(10), nullable=False)    
    street = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    last_update = Column(DateTime, default=func.now())

class ClientAdressesSQL(Base):
    __tablename__ = "client_adresse"
    id_client = Column(String(36), ForeignKey('clients.id_client'), primary_key=True)
    id_adresse = Column(String(36), ForeignKey('adresses.id_adresse'), primary_key=True)
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
        client_id = client["_id"]
        if "adresses" in client:
            for adresse in client["adresses"]:
                adresse_id = adresse["_id"]
                client_adresse = session.query(ClientAdressesSQL).filter_by(id_client=client_id, id_adresse=adresse_id).first()

                if client_adresse is None:
                    client_adresse = ClientAdressesSQL(id_client=client_id, id_adresse=adresse_id)
                    session.add(client_adresse)
                client_adresse.last_update = datetime.now()

    session.commit()

    
    
def synchronize_to_mongo():
    client_adresses = session.query(ClientAdressesSQL).all()

    for client_adresse in client_adresses:
        client = mongo_db.clients.find_one({"_id": client_adresse.id_client})
        adresse = mongo_db.adresses.find_one({"_id": client_adresse.id_adresse})

        if client and adresse:
            if "adresses" not in client or client_adresse.id_adresse not in [a["_id"] for a in client["adresses"]]:
                client.setdefault("adresses", []).append({
                    "_id": client_adresse.id_adresse,
                    "door": adresse.get("door"),
                    "street": adresse.get("street"),
                    "city": adresse.get("city"),
                    "postalCode": adresse.get("postal_code")
                })
                mongo_db.clients.update_one({"_id": client_adresse.id_client}, {"$set": client})

    
    
def resolve_conflicts():
    client_adresses_sql = session.query(ClientAdressesSQL).all()

    for client_adresse_sql in client_adresses_sql:
        client_mongo = mongo_db.clients.find_one({"_id": client_adresse_sql.id_client})
        adresse_mongo = None
        if client_mongo and "adresses" in client_mongo:
            adresse_mongo = next((adr for adr in client_mongo["adresses"] if adr["_id"] == client_adresse_sql.id_adresse), None)

        if adresse_mongo and "lastUpdate" in adresse_mongo:
            mongo_last_update = datetime.strptime(adresse_mongo["lastUpdate"], "%Y-%m-%dT%H:%M:%S.%fZ")
            sql_last_update = client_adresse_sql.last_update

            if mongo_last_update > sql_last_update:
                client_adresse_sql.last_update = mongo_last_update
            elif sql_last_update > mongo_last_update:
                adresse_mongo["lastUpdate"] = sql_last_update.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                mongo_db.clients.update_one({"_id": client_adresse_sql.id_client, "adresses._id": client_adresse_sql.id_adresse}, {"$set": {"adresses.$": adresse_mongo}})

    session.commit()

    
def synchroniser_clientAdresse():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation de client_adresse {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des client_adresse:", e)

