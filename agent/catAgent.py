import uuid
from bson import json_util
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["RCS"]

Base = declarative_base()

class CategorieSQL(Base):
    __tablename__ = 'categories'
    id_categorie = Column(String(36), primary_key=True)
    nom_categorie = Column(String(255), nullable=False)
    description_categorie = Column(String(255))
    last_update = Column(DateTime, default=func.now())

engine = create_engine('mysql+pymysql://root:@localhost/RCS')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def handle_sync_failure(uuid, filename="failed_syncs.txt"):
    with open(filename, "a") as file:
        file.write(uuid + "\n")


def synchronize_to_sql():
    categories = mongo_db.categories.find()

    for cat in categories:
        cat_sql = session.query(CategorieSQL).filter_by(id_categorie=cat["_id"]).first()

        if cat_sql is None:
            cat_sql = CategorieSQL(id_categorie=cat["_id"], nom_categorie=cat["nomCategorie"], description_categorie=cat["descriptionCategorie"])
            session.add(cat_sql)
        else:
            cat_sql.nom_categorie = cat["nomCategorie"]
            cat_sql.description_categorie = cat["descriptionCategorie"]
            cat_sql.last_update = datetime.now()
    session.commit()
        

def synchronize_to_mongo():
    categories = session.query(CategorieSQL).all()

    for cat in categories:
        cat_mongo = mongo_db.categories.find_one({"_id": cat.id_categorie})

        if cat_mongo is None:
            cat_mongo = {
                "_id": cat.id_categorie,
                "nomCategorie": cat.nom_categorie,
                "descriptionCategorie": cat.description_categorie,
                "lastUpdate": datetime.now()
            }
            mongo_db.categories.insert_one(cat_mongo)
        else:
            cat_mongo["nomCategorie"] = cat.nom_categorie
            cat_mongo["descriptionCategorie"] = cat.description_categorie
            cat_mongo["lastUpdate"] = datetime.now()
            mongo_db.categories.update_one({"_id": cat.id_categorie}, {"$set": cat_mongo})

    session.commit()


def resolve_conflicts():
    categories_mongo = mongo_db.categories.find()
    categories_sql = session.query(CategorieSQL).all()

    for cat_sql in categories_sql:
        cat_mongo = next((cat for cat in categories_mongo if cat["_id"] == cat_sql.id_categorie), None)

        if cat_mongo and "lastUpdate" in cat_mongo:
            mongo_lastUpdate = cat_mongo["lastUpdate"]
            sql_last_update = cat_sql.last_update or datetime.min

            if mongo_lastUpdate > sql_last_update:
                cat_sql.nom_categorie = cat_mongo["nomCategorie"]
                cat_sql.description_categorie = cat_mongo.get("descriptionCategorie", "")
                cat_sql.last_update = mongo_lastUpdate
            elif sql_last_update > mongo_lastUpdate:
                update_data = {
                    "nomCategorie": cat_sql.nom_categorie,
                    "descriptionCategorie": cat_sql.description_categorie,
                    "lastUpdate": sql_last_update
                }
                mongo_db.categories.update_one({"_id": cat_sql.id_categorie}, {"$set": update_data})

    session.commit()



def synchroniser_categorie():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation de la categorie {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des categories:", e)
