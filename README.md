# 🔥 Projet Chatrag  🔥 



## &#128203; Généralités :
Projet Django : chatbot orienté pour répondre en fonction d'une base documentaire (RAG: Retrieved Augmented Generation)

- python3.12
- django 5.2 
- poetry
- tailwind css v3
- base de données postgres
- base de données vectorielles pgvector
- docker : conteneurs web, db, ragdb, embedding
 

## &#8205;&#127891; Démonstration : [ici](#)

## 🤖 Fonctionnalités :
- ### Ingestion

    - documents textes : formats .pdf, .txt, .md
    - video youtubes (inclut la transcription)
    - split, vectorisation et enregistrement dans la bd vectorielle pg-vector

- ### Retrieval
    - à partir d'un prompt, recherche des meilleurs chunks

- ### Chat



## 🛠️ Installation : 

- ### cloner le projet :
```bash
    git clone https://xxxxxxxxx.git
```
- ### Mettre à jour les settings : SECRET_KEY, paramètres de base de donnée, noms de domaine, ports
    - créer settings/develop.py et settings/production.py : à parir des settings/develop.example.py et settings/production.example.py
    - créer .env : à partir de .env.example

- ### Déploiement en developpement:
```bash
    poetry install
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml build
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml up -d db dbrag
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml run --rm web src/manage.py migrate 
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml run --rm web src/manage.py createsuperuser
    # créer le superuser
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml run --rm web src/manage.py tailwind install
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml run --rm web src/manage.py tailwind start
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.override.yml up -d 
```

- ### Déploiement en production:

```bash
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml build
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.prod.yml up -d
    # entrypoint.sh exécute automatiquement: wait_for_db,migrate, collectstatic
    docker compose --env-file .env -f docker/docker-compose.yml -f docker/docker-compose.prod exec web python src/manage.py createsuperuser
    # créer le superuser
```

- ### Créer le 1er objet Collection
sur le site de l'administration, créer un objet Collection. Les champs sont documentés par défaut :

    - name:                 documents_chunk1000_bge-m3
    - is_active:            True
    - embedding model:      BAAI/bge-m3
    - chunk size:           1000
    - chunk overlap:        200
    - chunk number:         32 

## 🛢️ Voir directement les champs de la BD vectorielle :
```bash
# se connecter à la BD:
docker compose exec ragdb psql -U rag -d ragdb
```
```sql
-- table des collections:
select * from langchain_pg_collection;

-- table des embeddings(tronqué pour la lisibilité):
select 
    substring(id::text, 1, 5) || '...' as id,
    substring(collection_id::text, 1, 4) || '...' as col_id,
    left(embedding::text, 40) || '...]' as "embedding",
    left(document::text, 80) || '...' || right(document::text, 20) as "document chunk ~ 1000 caractères / 180 mots",
    left(cmetadata::text, 1) || '...' || right(cmetadata::text, 6) as cmetadata
    from langchain_pg_embedding;q;

-- dimension des vecteurs :
select 
    collection_id, vector_dims(embedding) as dimensions, 
    count(*) as nb_chunks
    from langchain_pg_embedding
group by collection_id, vector_dims(embedding);

-- taille min/max/moyenne des chunks en caratères et mots
select 
    min(length(document))  as chars_min,
    max(length(document))  as chars_max,
    avg(length(document))::int  as chars_avg,
    -- approximation mots : diviser par 5 (fr/en)
    avg(length(document) / 5)::int  as mots_avg
    from langchain_pg_embedding;

-- table des embeddings(tronqué pour la lisibilité):
select 
    substring(id::text, 1, 5) || '...' as id,
    left(embedding::text, 40) || '...]' as "embeddings",
    left(document::text, 75) || '...' || right(document::text, 15) as "document chunk",
    right(left(cmetadata::text, 42)::text,16) || '...' || right(cmetadata::text, 6) as cmetadata
    from langchain_pg_embedding;



```


