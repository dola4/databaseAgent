import uuid
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["RCS"]

Base = declarative_base()

class AdressesSQL(Base):
    __tablename__ = "adresses"
    id_adresse = Column(String(36), primary_key=True)
    door = Column(String(10), nullable=False)    
    street = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    last_update = Column(DateTime, default=func.now())
    
engine = create_engine('mysql+pymysql://root:@localhost/RCS')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def handle_sync_failure(uuid, filename="failed_syncs.txt"):
    with open(filename, "a") as file:
        file.write(uuid + "\n")


def synchronize_to_sql():
    adresses = mongo_db.adresses.find()
    
    for adr in adresses:
        adr_sql = session.query(AdressesSQL).filter_by(id_adresse=adr["_id"]).first()
        
        if adr_sql is None:
            adr_sql = AdressesSQL(id_adresse=adr["_id"], door=adr["door"], street=adr["street"], city=adr["city"], postal_code=adr["postal_code"])
            session.add(adr_sql)
        else:
            adr_sql.door = adr["door"]
            adr_sql.street = adr["street"]
            adr_sql.city = adr["city"]
            adr_sql.postal_code = adr["postal_code"]
            adr_sql.last_update = datetime.now()
    session.commit()
    
def synchronize_to_mongo():
    adresses = session.query(AdressesSQL).all()
    
    for adresse in adresses:
        adr_mongo = mongo_db.adresses.find_one({"_id": adresse.id_adresse})
        
        if adr_mongo is None:
            adr_mongo = {"_id": adresse.id_adresse, "door": adresse.door, "street": adresse.street, "city": adresse.city, "postal_code": adresse.postal_code}
            mongo_db.adresses.insert_one(adr_mongo)
        else:
            adr_mongo["door"] = adresse.door
            adr_mongo["street"] = adresse.street
            adr_mongo["city"] = adresse.city
            adr_mongo["postal_code"] = adresse.postal_code
            adr_mongo["lastUpdate"] = datetime.now()
        
        mongo_db.adresses.update_one({"_id": adresse.id_adresse}, {"$set": adr_mongo})
        
def resolve_conflicts():
    adresses_sql = session.query(AdressesSQL).all()

    for adresse_sql in adresses_sql:
        adresse_mongo = mongo_db.adresses.find_one({"_id": adresse_sql.id_adresse})

        if adresse_mongo:
            sql_last_update = adresse_sql.last_update
            mongo_last_update = adresse_mongo.get("lastUpdate")

            if mongo_last_update and isinstance(mongo_last_update, str):
                mongo_last_update = datetime.strptime(mongo_last_update, "%Y-%m-%dT%H:%M:%S.%fZ")

            if sql_last_update and mongo_last_update:
                if sql_last_update > mongo_last_update:
                    update_data = {
                        "door": adresse_sql.door,
                        "street": adresse_sql.street,
                        "city": adresse_sql.city,
                        "postal_code": adresse_sql.postal_code,
                        "lastUpdate": sql_last_update.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    }
                    mongo_db.adresses.update_one({"_id": adresse_sql.id_adresse}, {"$set": update_data})
                elif mongo_last_update > sql_last_update:
                    adresse_sql.door = adresse_mongo["door"]
                    adresse_sql.street = adresse_mongo["street"]
                    adresse_sql.city = adresse_mongo["city"]
                    adresse_sql.postal_code = adresse_mongo["postal_code"]
                    adresse_sql.last_update = mongo_last_update

    session.commit()


def synchroniser_adresse():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation de l'adresse {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des adresses:", e)

