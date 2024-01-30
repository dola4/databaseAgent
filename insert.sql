INSERT INTO clients (id_client, nom, prenom, email, mot2passe, last_update) 
VALUES 
('d1aa62db-309b-4c01-bccc-5302feec598e', 'Nom1', 'Prenom1', 'email1@example.com', 'password1', NOW()),
('09e03ad9-d99b-44b5-a58e-1a92d86ab3b0', 'Nom2', 'Prenom2', 'email2@example.com', 'password2', NOW()),
('2de82517-a1e6-4ff5-befc-fb2f2e5e73e7', 'Nom3', 'Prenom3', 'email3@example.com', 'password3', NOW()),
('05422a0d-b490-4e49-9b57-d547c6889efb', 'Nom4', 'Prenom4', 'email4@example.com', 'password4', NOW()),
('48f66b1f-d056-4ae6-97e9-70f904c7b471', 'Nom5', 'Prenom5', 'email5@example.com', 'password5', NOW());

INSERT INTO adresses (id_adresse, door, street, city, postal_code, last_update) 
VALUES 
('f343c09b-b3e1-45d2-a2ff-b36a39b9abfd', '10', "Rue de l\'Exemple", 'Ville1', '10000', NOW()),
('eeaea405-3adc-4f5c-86d1-e4f0f6100b7d', '20', 'Avenue de la Liberté', 'Ville2', '20000', NOW()),
('ad0b5bed-9654-4486-a7c3-9acb914fd644', '30', 'Chemin des Oliviers', 'Ville3', '30000', NOW()),
('4e46bfb1-30ad-46d7-a6b1-a87372cf6366', '40', 'Boulevard de la Mer', 'Ville4', '40000', NOW()),
('3e558b36-2bd7-41a4-b332-a98671feb0b6', '50', 'Rue des Peupliers', 'Ville5', '50000', NOW());

INSERT INTO client_adresse (id_client, id_adresse, last_update) 
VALUES 
('d1aa62db-309b-4c01-bccc-5302feec598e', 'f343c09b-b3e1-45d2-a2ff-b36a39b9abfd', NOW()),
('09e03ad9-d99b-44b5-a58e-1a92d86ab3b0', 'eeaea405-3adc-4f5c-86d1-e4f0f6100b7d', NOW()),
('2de82517-a1e6-4ff5-befc-fb2f2e5e73e7', 'ad0b5bed-9654-4486-a7c3-9acb914fd644', NOW()),
('05422a0d-b490-4e49-9b57-d547c6889efb', '4e46bfb1-30ad-46d7-a6b1-a87372cf6366', NOW()),
('48f66b1f-d056-4ae6-97e9-70f904c7b471', '3e558b36-2bd7-41a4-b332-a98671feb0b6', NOW());

INSERT INTO commandes (id_commande, id_client, id_adresse, date_commande, total, last_update) 
VALUES 
('a7f0d958-3d7f-4703-835b-7b4c849dfc40', 'd1aa62db-309b-4c01-bccc-5302feec598e', 'f343c09b-b3e1-45d2-a2ff-b36a39b9abfd', '2023-01-01', 100.0, NOW()),
('66b65d93-641f-4b65-b51d-b7f68d34cf7e', '09e03ad9-d99b-44b5-a58e-1a92d86ab3b0', 'eeaea405-3adc-4f5c-86d1-e4f0f6100b7d', '2023-02-01', 200.0, NOW()),
('d302877e-8156-4f42-96d2-c5e261795bcb', '2de82517-a1e6-4ff5-befc-fb2f2e5e73e7', 'ad0b5bed-9654-4486-a7c3-9acb914fd644', '2023-03-01', 300.0, NOW()),
('5c61b816-b28e-47cf-bb9a-ca75f98f9251', '05422a0d-b490-4e49-9b57-d547c6889efb', '4e46bfb1-30ad-46d7-a6b1-a87372cf6366', '2023-04-01', 400.0, NOW()),
('4c358a2b-68f8-4f6f-8e02-05cfe8f6e543', '48f66b1f-d056-4ae6-97e9-70f904c7b471', '3e558b36-2bd7-41a4-b332-a98671feb0b6', '2023-05-01', 500.0, NOW());

INSERT INTO categories (id_categorie, nom_categorie, description_categorie, last_update) 
VALUES 
('3b0349c1-f316-4143-afad-8d302515a4a8', 'Catégorie1', 'Description1', NOW()),
('0045b8cb-5c69-42b6-987b-a77f99bfc8f5', 'Catégorie2', 'Description2', NOW()),
('c51bbb3a-bdb1-4d5d-8168-72dd952cc769', 'Catégorie3', 'Description3', NOW()),
('1fcda3af-32d1-48ee-868b-9918ce889140', 'Catégorie4', 'Description4', NOW()),
('96d78ae0-c1fc-4e90-aecd-593c6f91970c', 'Catégorie5', 'Description5', NOW());

INSERT INTO produits (id_produit, id_categorie, nom_produit, prix, image, last_update) 
VALUES 
('d553fdf3-8731-4fa2-8234-b4d29c867505', '3b0349c1-f316-4143-afad-8d302515a4a8', 'Produit1', 10.0, 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.ikea.com%2Ffr%2Ffr%2Fp%2Fmelltorp-table-blanc-80290223%2F&psig=AOvVaw0Z3Z3X6Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3&ust=1614829865762000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJjQ4ZqM9-8CFQAAAAAdAAAAABAJ', NOW()),
('c8dd852e-b861-4fa1-846b-4b7995d83c72', '0045b8cb-5c69-42b6-987b-a77f99bfc8f5', 'Produit2', 20.0, 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.ikea.com%2Ffr%2Ffr%2Fp%2Fmelltorp-table-blanc-80290223%2F&psig=AOvVaw0Z3Z3X6Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3&ust=1614829865762000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJjQ4ZqM9-8CFQAAAAAdAAAAABAJ', NOW()),
('206aec9e-6367-4a4d-9812-a3d3118e58e4', 'c51bbb3a-bdb1-4d5d-8168-72dd952cc769', 'Produit3', 30.0, 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.ikea.com%2Ffr%2Ffr%2Fp%2Fmelltorp-table-blanc-80290223%2F&psig=AOvVaw0Z3Z3X6Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3&ust=1614829865762000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJjQ4ZqM9-8CFQAAAAAdAAAAABAJ', NOW()),
('d3bd337e-59d3-440c-ba2b-ceb6f619083f', '1fcda3af-32d1-48ee-868b-9918ce889140', 'Produit4', 40.0, 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.ikea.com%2Ffr%2Ffr%2Fp%2Fmelltorp-table-blanc-80290223%2F&psig=AOvVaw0Z3Z3X6Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3&ust=1614829865762000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJjQ4ZqM9-8CFQAAAAAdAAAAABAJ', NOW()),
('83594a6e-f57c-47b0-a1aa-114d9fb7570b', '96d78ae0-c1fc-4e90-aecd-593c6f91970c', 'Produit5', 50.0, 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.ikea.com%2Ffr%2Ffr%2Fp%2Fmelltorp-table-blanc-80290223%2F&psig=AOvVaw0Z3Z3X6Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3Z3&ust=1614829865762000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCJjQ4ZqM9-8CFQAAAAAdAAAAABAJ', NOW());

INSERT INTO commande_produit (id_commande, id_produit, quantite, last_update) 
VALUES 
('a7f0d958-3d7f-4703-835b-7b4c849dfc40', 'd553fdf3-8731-4fa2-8234-b4d29c867505', 1, NOW()),
('66b65d93-641f-4b65-b51d-b7f68d34cf7e', 'c8dd852e-b861-4fa1-846b-4b7995d83c72', 2, NOW()),
('d302877e-8156-4f42-96d2-c5e261795bcb', '206aec9e-6367-4a4d-9812-a3d3118e58e4', 3, NOW()),
('5c61b816-b28e-47cf-bb9a-ca75f98f9251', 'd3bd337e-59d3-440c-ba2b-ceb6f619083f', 4, NOW()),
('4c358a2b-68f8-4f6f-8e02-05cfe8f6e543', '83594a6e-f57c-47b0-a1aa-114d9fb7570b', 5, NOW())

