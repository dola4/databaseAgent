CREATE DATABASE IF NOT EXISTS RCS;

USE RCS;

CREATE TABLE IF NOT EXISTS clients (
    id_client VARCHAR(36) NOT NULL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    mot2passe VARCHAR(255) NOT NULL,
    last_update DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS adresses (
    id_adresse VARCHAR(36) NOT NULL PRIMARY KEY,
    door VARCHAR(10) NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    postal_code VARCHAR(255) NOT NULL,
    last_update DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS client_adresse (
    id_client VARCHAR(36) NOT NULL,
    id_adresse VARCHAR(36) NOT NULL,
    last_update DATETIME NOT NULL,
    FOREIGN KEY (id_client) REFERENCES clients(id_client),
    FOREIGN KEY (id_adresse) REFERENCES adresses(id_adresse)
);



CREATE TABLE IF NOT EXISTS categories(
    id_categorie VARCHAR(36) NOT NULL PRIMARY KEY,
    nom_categorie VARCHAR(255) NOT NULL,
    description_categorie VARCHAR(255) NOT NULL,
    last_update DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS commandes(
    id_commande VARCHAR(36) NOT NULL PRIMARY KEY,
    id_client VARCHAR(36) NOT NULL,
    id_adresse VARCHAR(36) NOT NULL,
    date_commande DATETIME NOT NULL,
    total FLOAT NOT NULL,
    last_update DATETIME NOT NULL,
    FOREIGN KEY (id_client) REFERENCES clients(id_client),
    FOREIGN KEY (id_adresse) REFERENCES adresses(id_adresse)
);

CREATE TABLE IF NOT EXISTS produits(
    id_produit VARCHAR(36) NOT NULL PRIMARY KEY,
    id_categorie VARCHAR(36) NOT NULL,
    nom_produit VARCHAR(255) NOT NULL,
    prix FLOAT NOT NULL,    
    image VARCHAR(255) NOT NULL,
    last_update DATETIME NOT NULL,
    FOREIGN KEY (id_categorie) REFERENCES categories(id_categorie)
);

CREATE TABLE IF NOT EXISTS commande_produit(
    id_commande VARCHAR(36) NOT NULL,
    id_produit VARCHAR(36) NOT NULL,
    quantite INT NOT NULL,
    last_update DATETIME NOT NULL,
    FOREIGN KEY (id_commande) REFERENCES commandes(id_commande),
    FOREIGN KEY (id_produit) REFERENCES produits(id_produit)
);
