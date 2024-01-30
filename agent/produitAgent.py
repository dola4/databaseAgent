import uuid
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["RCS"]

Base = declarative_base()

class ProduitSQL(Base):
    __tablename__ = 'produits'
    id_produit = Column(String(36), primary_key=True)
    id_categorie = Column(String(36), nullable=False)
    nom_produit = Column(String(255), nullable=False)
    prix = Column(String(255))
    image = Column(String(255))
    last_update = Column(DateTime, default=func.now())


engine = create_engine('mysql+pymysql://root:@localhost/RCS')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def handle_sync_failure(uuid, filename="failed_syncs.txt"):
    with open(filename, "a") as file:
        file.write(uuid + "\n")

def synchronize_to_sql():
    produits = mongo_db.produits.find()

    for prod in produits:
        prod_sql = session.query(ProduitSQL).filter_by(id_produit=prod["_id"]).first()

        if prod_sql is None:
            prod_sql = ProduitSQL(id_produit=prod["_id"], id_categorie=prod["categorieId"], nom_produit=prod["nomProduit"], prix=prod["prix"], image=prod["image"])
            session.add(prod_sql)
        else:
            prod_sql.id_categorie = prod["categorieId"]
            prod_sql.nom_produit = prod["nomProduit"]
            prod_sql.prix = prod["prix"]
            prod_sql.image = prod["image"]
            prod_sql.last_update = datetime.now()
    
    session.commit()

def synchronize_to_mongo():
    produits = session.query(ProduitSQL).all()

    for prod in produits:
        prod_mongo = mongo_db.produits.find_one({"_id": prod.id_produit})

        if prod_mongo is None:
            prod_mongo = {
                "_id": prod.id_produit, 
                "categorieId": prod.id_categorie, 
                "nomProduit": prod.nom_produit, 
                "prix": prod.prix, 
                "image": prod.image,
                "lastUpdate": datetime.now() 
            }
            mongo_db.produits.insert_one(prod_mongo)
        else:
            prod_mongo["categorieId"] = prod.id_categorie
            prod_mongo["nomProduit"] = prod.nom_produit
            prod_mongo["prix"] = prod.prix
            prod_mongo["image"] = prod.image
            prod_mongo["lastUpdate"] = datetime.now() 

            mongo_db.produits.update_one({"_id": prod.id_produit}, {"$set": prod_mongo})

    session.commit()



def resolve_conflicts():
    produits = session.query(ProduitSQL).all()

    for prod in produits:
        prod_mongo = mongo_db.produits.find_one({"_id": prod.id_produit})

        if prod_mongo and "lastUpdate" in prod_mongo:
            if prod.last_update > prod_mongo["lastUpdate"]:
                prod_mongo["categorieId"] = prod.id_categorie
                prod_mongo["nomProduit"] = prod.nom_produit
                prod_mongo["prix"] = prod.prix
                prod_mongo["image"] = prod.image
                prod_mongo["lastUpdate"] = datetime.now()

                mongo_db.produits.update_one({"_id": prod.id_produit}, {"$set": prod_mongo})
            else:
                prod.id_categorie = prod_mongo["categorieId"]
                prod.nom_produit = prod_mongo["nomProduit"]
                prod.prix = prod_mongo["prix"]
                prod.image = prod_mongo["image"]
                prod.last_update = prod_mongo["lastUpdate"]

    session.commit()



def synchroniser_produit():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation du produit {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des produits:", e)