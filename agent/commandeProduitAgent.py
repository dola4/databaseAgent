import uuid
import json
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func, ForeignKey, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, time
from dateutil import parser


mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["RCS"]

Base = declarative_base()


class CommandSql(Base):
    __tablename__ = "commandes"
    id_commande = Column(String(36), primary_key=True)
    id_client = Column(String(36), nullable=False)
    id_adresse = Column(String(36), nullable=False)
    date_commande = Column(DateTime, default=func.now())
    total = Column(Float, nullable=False)
    last_update = Column(DateTime, default=func.now())
    
class ProduitSQL(Base):
    __tablename__ = 'produits'
    id_produit = Column(String(36), primary_key=True)
    id_categorie = Column(String(36), nullable=False)
    nom_produit = Column(String(255), nullable=False)
    prix = Column(Float, nullable=False)
    image = Column(String(255), nullable=False)
    last_update = Column(DateTime, default=func.now())

class commande_produitSQL(Base):
    __tablename__ = "commande_produit"
    id_commande = Column(String(36), ForeignKey("commandes.id_commande"), primary_key=True)
    id_produit = Column(String(36), ForeignKey("produits.id_produit"), primary_key=True)
    quantite = Column(Integer, nullable=False)
    last_update = Column(DateTime, default=func.now())

    
engine = create_engine('mysql+pymysql://root:@localhost/RCS')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def handle_sync_failure(uuid, filename="failed_syncs.txt"):
    with open(filename, "a") as file:
        file.write(uuid + "\n")

def synchronize_to_sql():
    commandes = mongo_db.commandes.find()
    print("Début de la synchronisation vers SQL")

    for commande in commandes:
        commande_id = commande['_id']
        print(f"Traitement de la commande: {commande_id}")
        

        if 'produits' in commande and 'quantite' in commande:
            produit = commande['produits']
            quantite = commande['quantite']

            if isinstance(produit, dict) and '_id' in produit:
                produit_id = produit['_id']
                print(f"Traitement du produit {produit_id} dans la commande {commande_id}")

                commande_produit_sql = session.query(commande_produitSQL).filter_by(id_commande=commande_id, id_produit=produit_id).first()
                if not commande_produit_sql:
                    commande_produit_sql = commande_produitSQL(
                        id_commande=commande_id,
                        id_produit=produit_id,
                        quantite=quantite, 
                        last_update=datetime.now()
                    )
                    session.add(commande_produit_sql)
                else:
                    commande_produit_sql.quantite = quantite
                    commande_produit_sql.last_update = datetime.now()
            else:
                print(f"Format inattendu pour le produit dans la commande {commande_id}")

    session.commit()
    print("Fin de la synchronisation vers SQL")



def synchronize_to_mongo():
    commandes_sql = session.query(CommandSql).all()
    print("Début de la synchronisation vers MongoDB")

    for cmd_sql in commandes_sql:
        commande_data = {
            "id_client": cmd_sql.id_client,
            "id_adresse": cmd_sql.id_adresse,
            "dateCommande": cmd_sql.date_commande.isoformat(),
            "total": cmd_sql.total,
            "lastUpdate": cmd_sql.last_update.isoformat()
        }

        commande_mongo = mongo_db.commandes.find_one({"_id": cmd_sql.id_commande})
        if commande_mongo is None:
            mongo_db.commandes.insert_one({"_id": cmd_sql.id_commande, **commande_data})
        else:
            mongo_db.commandes.update_one({"_id": cmd_sql.id_commande}, {"$set": commande_data})

        commande_produits_sql = session.query(commande_produitSQL).filter_by(id_commande=cmd_sql.id_commande).all()
        for cp_sql in commande_produits_sql:
            produit_data = {
                "id_produit": cp_sql.id_produit,
                "quantite": cp_sql.quantite,
                "lastUpdate": cp_sql.last_update.isoformat()
            }

            if commande_mongo:
                produits_mongo = commande_mongo.get("produits", [])
                if isinstance(produits_mongo, str):
                    try:
                        produits_mongo = json.loads(produits_mongo)
                    except json.JSONDecodeError:
                        print(f"Erreur de décodage JSON pour les produits dans la commande {cmd_sql.id_commande}")
                        continue

                produit_existe = False
                for produit in produits_mongo:
                    if produit.get("id_produit") == cp_sql.id_produit:
                        produit.update(produit_data)
                        produit_existe = True
                        break
                if not produit_existe:
                    produits_mongo.append(produit_data)
                
                mongo_db.commandes.update_one({"_id": cmd_sql.id_commande}, {"$set": {"produits": produits_mongo}})
            else:
                mongo_db.commandes.update_one({"_id": cmd_sql.id_commande}, {"$set": {"produits": [produit_data]}})

            print(f"Mise à jour du produit {cp_sql.id_produit} pour la commande {cmd_sql.id_commande} dans MongoDB")

    session.commit()
    print("Fin de la synchronisation vers MongoDB")





def resolve_conflicts():
    commandes_sql = session.query(CommandSql).all()

    for cmd_sql in commandes_sql:
        commande_mongo = mongo_db.commandes.find_one({"_id": cmd_sql.id_commande})

        if commande_mongo:
            mongo_last_update = commande_mongo.get("lastUpdate")

            if isinstance(mongo_last_update, str):
                try:
                    mongo_last_update = parser.parse(mongo_last_update)
                except ValueError:
                    print(f"Format de date invalide pour la dernière mise à jour de MongoDB: {mongo_last_update}")
                    continue
            sql_last_update = cmd_sql.last_update
            if isinstance(sql_last_update, date):
                sql_last_update = datetime.combine(sql_last_update, time())

            if mongo_last_update and sql_last_update:
                if mongo_last_update > sql_last_update:
                    cmd_sql.id_client = commande_mongo["id_client"]
                    cmd_sql.id_adresse = commande_mongo["id_adresse"]
                    cmd_sql.date_commande = commande_mongo["dateCommande"]
                    cmd_sql.total = commande_mongo["total"]
                    cmd_sql.last_update = mongo_last_update
                elif sql_last_update > mongo_last_update:
                    update_data = {
                        "id_client": cmd_sql.id_client,
                        "id_adresse": cmd_sql.id_adresse,
                        "dateCommande": cmd_sql.date_commande.isoformat(),
                        "total": cmd_sql.total,
                        "lastUpdate": sql_last_update.isoformat()
                    }
                    mongo_db.commandes.update_one({"_id": cmd_sql.id_commande}, {"$set": update_data})

        commande_produits_sql = session.query(commande_produitSQL).filter_by(id_commande=cmd_sql.id_commande).all()
        for cp_sql in commande_produits_sql:
            commande_mongo = mongo_db.commandes.find_one({"_id": cp_sql.id_commande})
            if commande_mongo and "produits" in commande_mongo:
                produit_mongo = next((p for p in commande_mongo["produits"] if p.get("id_produit") == cp_sql.id_produit), None)
                if produit_mongo:
                    mongo_last_update = produit_mongo.get("lastUpdate")
                    if isinstance(mongo_last_update, str):
                        mongo_last_update = parser.parse(mongo_last_update)

                    sql_last_update = cp_sql.last_update
                    if isinstance(sql_last_update, date):
                        sql_last_update = datetime.combine(sql_last_update, time())

                    if mongo_last_update and sql_last_update:
                        if mongo_last_update > sql_last_update:
                            cp_sql.quantite = produit_mongo["quantite"]
                            cp_sql.last_update = mongo_last_update
                        elif sql_last_update > mongo_last_update:
                            update_data = {
                                "quantite": cp_sql.quantite,
                                "lastUpdate": sql_last_update.isoformat()
                            }
                            mongo_db.commandes.update_one({"_id": cp_sql.id_commande, "produits.id_produit": cp_sql.id_produit}, {"$set": {"produits.$": update_data}})

    session.commit()
    print("Fin de la résolution des conflits")


def synchroniser_commandeProduit():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation de commande_produit {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des commande_produit:", e)

    
