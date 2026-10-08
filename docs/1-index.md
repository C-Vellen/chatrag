# 1- Présentation générale
## 1-1- Description
Interface conversationnelle basée sur un RAG (Retrieval Augmented Generation) :

- interface d'administration permettant de se connecter aux bases documentaires et d'ingérer de nouveaux documents.
- Interface conversationnelle répondant à une requâte de l'uitilisateur. La réponse est basée sur les bases documentaires ingérées. Les conversations peuvent être enregistrées sur le compte de l'utilisateur.
- Interface de test permettant de mesurer la performance des réponses à partir d'un jeu de test.


## 1-2- Architecture globale


![](img/archi_globale.drawio)






## 1-3- Stack technique

Technologies utilisées

| Couche | Technologie |	Version majeure	| Rôle|
|---|---|---|---|
| Framework web | Django |	5.2 |	Application, ORM, administration, authentification|
| Orchestration RAG |	LangChain |	1.3 |	Chaîne de récupération et de génération |
| Intégration vectorielle |	langchain-postgres |	0.0 |	Interface LangChain vers pgvector |
| Base de données |	PostgreSQL |	16 |	Données applicatives et vecteurs |
| Extension vectorielle |	pgvector |	16 |	Stockage et recherche de similarité |
| Modèle d'embedding |	BAAI/bge-m3 |latest |	Vectorisation des chunks et des requêtes |
| LLM de génération |	à compléter |	— |	Génération des réponses |
| Tâches asynchrones |	Celery |x.x |	Ingestion des documents en arrière-plan |
| Broker / cache |	Redis |	7.x  |	File de messages Celery |
| Streaming |	Server-Sent Events (SSE) |	— |	Affichage progressif des réponses du chat |
| Conteneurisation |	Docker, docker compose |	— |	Déploiement et environnement de développement |