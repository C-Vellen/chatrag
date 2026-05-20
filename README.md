# 🔥 Projet Chatrag  🔥 



## &#128203; Généralités :
Projet Django : chatbot orienté pour répondre en fonction d'une base documentaire (RAG: Retrieved Augmented Generation)

- python3.12
- django 5.2 
- poetry
- tailwind css v3
- base de données postgres
- Docker : conteneurs web, tailwind, db
 

##  &#8205;&#127891; Démonstration : [ici](https://www.xxxxxx.fr)

## &#129520; Fonctionnalités :
- ### Fonctionnalités ...

## &#129489;&#8205;&#127891; Les utilisateurs :
- ### ...

## &#128736; Installation : 

- settings : 
  - créer settings/develop.py et settings/production.py : voir les modèles settings/develop.example.py et settings/production.example.py
  - créer .env pour les paramètres de la bd et les variables d'environnement utiles (TOKEN_API...)
- cloner le projet :
```bash
    git clone https://xxxxxxxxx.git
```
- installation en dev:
```bash
    
```
- installation en prod:
```bash
    d
```

### Voir la BD vectorielle :
```bash
# se connecter à la BD:
docker compose exec ragdb psql -U rag -d ragdb
```
```sql
-- table des collections:
select * from langchain_pg_collection

-- table des embeddings(tronqué pour la lisibilité):
select 
    substring(id::text, 1, 5) || '...' as id,
    substring(collection_id::text, 1, 4) || '...' as col_id,
    left(embedding::text, 40) || '...]' as "embedding",
    left(document::text, 80) || '...' || right(document::text, 20) as "document chunk ~ 1000 caractères / 180 mots",
    left(cmetadata::text, 1) || '...' || right(cmetadata::text, 6) as cmetadata
    from langchain_pg_embedding;q

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


