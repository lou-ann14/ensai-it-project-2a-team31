-- Comptes de test : admin / 123, collaborateur / 456, client / 789
-- Les mots de passe sont hachés comme dans UtilisateurService : hash_password(mdp, nom_utilisateur)
INSERT INTO utilisateurs(nom_utilisateur, mdp, grade) VALUES
('admin', '82a79f11b4acb52a642ef7e339dfce4aa92ff65ed2e7ab702d798dbe10eca0b8', 'ADMIN'),
('collaborateur', '1bb3556b599c004027211a303c6a14ea68f6b261f5f516847dcfd816904edb29', 'COLLABORATEUR'),
('client', 'a4b19f72bac99ab0bc8faba555b167b86b8f8b5f3b2289cbbfd462972ed595b5', 'CLIENT');
