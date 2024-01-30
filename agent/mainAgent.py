from pymongo import MongoClient
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from datetime import datetime

from adressesAgent import synchroniser_adresse, AdressesSQL
from catAgent import synchroniser_categorie, CategorieSQL
from clientAdresseAgent import synchroniser_clientAdresse, ClientAdressesSQL
from clientAgent import synchroniser_client, ClientSQL
from commandAgent import synchroniser_command, CommandSql
from commandeProduitAgent import synchroniser_commandeProduit, commande_produitSQL
from produitAgent import synchroniser_produit, ProduitSQL

client = MongoClient("mongodb://localhost:27017/")
db = client["RCS"]


def start_thread_as_daemon(target, args):
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    return thread

def poll_mongo_changes(collection_name, sync_function, interval=1):
    print(f"Démarrage du polling pour la collection MongoDB {collection_name}")
    collection = db[collection_name]
    last_checked = datetime.min

    while True:
        try:
            query = {"lastUpdate": {"$gt": last_checked}}
            count = db[collection_name].count_documents(query)  

            if count > 0:
                print(f"Changements détectés dans MongoDB {collection_name}")
                sync_function()

            last_checked = datetime.now()
        except Exception as e:
            print(f"Erreur lors du polling MongoDB {collection_name}:", e)

        time.sleep(interval)


thread_adresse = start_thread_as_daemon(target=poll_mongo_changes, args=("adresses", synchroniser_adresse))
thread_categorie = start_thread_as_daemon(target=poll_mongo_changes, args=("categories", synchroniser_categorie))
thread_cliAdesse = start_thread_as_daemon(target=poll_mongo_changes, args=("clientAdresse", synchroniser_clientAdresse))
thread_clients = start_thread_as_daemon(target=poll_mongo_changes, args=("clients", synchroniser_client))
thread_commandes = start_thread_as_daemon(target=poll_mongo_changes, args=("commandes", synchroniser_command))
thread_commandProduit = start_thread_as_daemon(target=poll_mongo_changes, args=("commandeProduit", synchroniser_commandeProduit))
thread_produit = start_thread_as_daemon(target=poll_mongo_changes, args=("produits", synchroniser_produit))


def listen_sql_changes():
    print("Démarrage de l'écoute pour la base de données SQL.")
    engine = create_engine('mysql+pymysql://root:@localhost/RCS')
    Session = sessionmaker(bind=engine)
    session = Session()

    last_checked = datetime.min
    while True:
        session = sessionmaker(bind=engine)()
        try:
            for table, sync_function in [
                (AdressesSQL, synchroniser_adresse),
                (CategorieSQL, synchroniser_categorie),
                (ClientAdressesSQL, synchroniser_clientAdresse),
                (ClientSQL, synchroniser_client),
                (CommandSql, synchroniser_command),
                (commande_produitSQL, synchroniser_commandeProduit),
                (ProduitSQL, synchroniser_produit)
            ]:
                print(f"Vérification des changements pour {table.__tablename__}")
                query = session.query(table).filter(table.last_update > last_checked)
                results = query.all()

                if results:
                    print(f"Changement détecté dans la base de données SQL {table.__tablename__}")
                    sync_function()

            last_checked = datetime.now()
        except Exception as e:
            print("Erreur lors de l'écoute SQL:", e)
        time.sleep(1)
thread_sql = start_thread_as_daemon(target=listen_sql_changes, args=())


if __name__ == "__main__":
    thread_adresse.start()
    thread_categorie.start()
    thread_cliAdesse.start()
    thread_clients.start()
    thread_commandes.start()
    thread_commandProduit.start()
    thread_produit.start()
    thread_sql.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du script par l'utilisateur.")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
    finally:
        print("Script principal terminé.")