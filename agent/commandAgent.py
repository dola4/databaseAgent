import uuid
from pymongo import MongoClient
from sqlalchemy import create_engine, Column, String, DateTime, func, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
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
    
engine = create_engine('mysql+pymysql://root:@localhost/RCS')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def handle_sync_failure(uuid, filename="failed_syncs.txt"):
    with open(filename, "a") as file:
        file.write(uuid + "\n")

def synchronize_to_sql():
    commandes = mongo_db.commandes.find()
    
    for cmd in commandes:
        cmd_sql = session.query(CommandSql).filter_by(id_commande=cmd["_id"]).first()
        
        if cmd_sql is None:
            cmd_sql = CommandSql(id_commande=cmd["_id"], id_client=cmd["id_client"], id_adresse=cmd["id_adresse"], date_commande=cmd["dateCommande"], total=cmd["total"])
            session.add(cmd_sql)
        else:
            cmd_sql.id_client = cmd["id_client"]
            cmd_sql.id_adresse = cmd["id_adresse"]
            cmd_sql.date_commande = cmd["dateCommande"]
            cmd_sql.total = cmd["total"]
            cmd_sql.last_update = datetime.now()
    session.commit()

def synchronize_to_mongo():
    commandes = session.query(CommandSql).all()
    
    for cmd in commandes:
        cmd_mongo = mongo_db.commandes.find_one({"_id": cmd.id_commande})
        last_update_iso = cmd.last_update.isoformat()

        if cmd_mongo is None:
            cmd_mongo = {
                "_id": cmd.id_commande,
                "id_client": cmd.id_client,
                "id_adresse": cmd.id_adresse,
                "dateCommande": cmd.date_commande.isoformat(),
                "total": cmd.total,
                "lastUpdate": last_update_iso
            }
            mongo_db.commandes.insert_one(cmd_mongo)
        else:
            mongo_db.commandes.update_one(
                {"_id": cmd.id_commande},
                {"$set": {
                    "id_client": cmd.id_client,
                    "id_adresse": cmd.id_adresse,
                    "dateCommande": cmd.date_commande.isoformat(),
                    "total": cmd.total,
                    "lastUpdate": last_update_iso
                }}
            )

    session.commit()

        
def resolve_conflicts():
    commandes_sql = session.query(CommandSql).all()

    for cmd_sql in commandes_sql:
        cmd_mongo = mongo_db.commandes.find_one({"_id": cmd_sql.id_commande})

        if cmd_mongo:
            mongo_last_update = cmd_mongo.get("lastUpdate")
            if mongo_last_update:
                mongo_last_update = parser.parse(mongo_last_update)

            if cmd_sql.last_update > mongo_last_update:
                update_data = {
                    "id_client": cmd_sql.id_client,
                    "id_adresse": cmd_sql.id_adresse,
                    "dateCommande": cmd_sql.date_commande.isoformat(),
                    "total": cmd_sql.total,
                    "lastUpdate": cmd_sql.last_update.isoformat()
                }
                mongo_db.commandes.update_one({"_id": cmd_sql.id_commande}, {"$set": update_data})
            elif mongo_last_update > cmd_sql.last_update:
                cmd_sql.id_client = cmd_mongo["id_client"]
                cmd_sql.id_adresse = cmd_mongo["id_adresse"]
                cmd_sql.date_commande = mongo_last_update
                cmd_sql.total = cmd_mongo["total"]
                cmd_sql.last_update = mongo_last_update

    session.commit()
def synchroniser_command():
    try:
        failed_uuid = synchronize_to_sql() or synchronize_to_mongo() or resolve_conflicts()
        if failed_uuid:
            handle_sync_failure(failed_uuid)
            print(f"Erreur lors de la synchronisation de la commande {failed_uuid}")
    except Exception as e:
        print("Erreur lors de la synchronisation des commandes:", e)
