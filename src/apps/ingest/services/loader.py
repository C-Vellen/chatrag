from pathlib import Path
from typing import Union
from django.core.files.uploadedfile import UploadedFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_core.documents import Document
import tempfile
import os


def load_from_path(source: str | Path) -> list[Document]:
    """Charge depuis un chemin fichier ou dossier."""
    source = Path(source)

    if source.is_dir():
        loaders = [
            DirectoryLoader(str(source), glob="**/*.pdf", loader_cls=PyPDFLoader),
            DirectoryLoader(str(source), glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(str(source), glob="**/*.md",  loader_cls=TextLoader),
        ]
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
        return docs

    suffix = source.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(source)).load()
    elif suffix in (".txt", ".md"):
        return TextLoader(str(source)).load()
    else:
        raise ValueError(f"Format non supporté : {suffix}")


def load_from_upload(file: UploadedFile) -> list[Document]:
    """
    Charge depuis un objet UploadedFile Django.
    Ecrit temporairement le fichier sur disque car les loaders
    LangChain ont besoin d'un chemin fichier.
    """
    suffix = Path(file.name).suffix.lower()

    if suffix not in (".pdf", ".txt", ".md"):
        raise ValueError(f"Format non supporté : {suffix}")

    # Ecriture dans un fichier temporaire
    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False
    ) as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            docs = PyPDFLoader(tmp_path).load()
        else:
            docs = TextLoader(tmp_path).load()

        # Remplacer le chemin temporaire par le nom original dans les métadonnées
        for doc in docs:
            doc.metadata["source"] = file.name

    finally:
        os.unlink(tmp_path)  # supprime le fichier temporaire dans tous les cas

    return docs


def load_from_dict(data: dict) -> list[Document]:
    """
    Charge depuis un dictionnaire avec les clés :
      - "titre"   : titre du document (utilisé dans les métadonnées)
      - "content" : contenu texte du document
    """
    if "content" not in data:
        raise ValueError("Le dictionnaire doit contenir la clé 'content'.")
    if "titre" not in data:
        raise ValueError("Le dictionnaire doit contenir la clé 'titre'.")

    titre   = data["titre"]
    content = data["content"]

    if not content.strip():
        raise ValueError(f"Le contenu de '{titre}' est vide.")

    # Ecriture dans un fichier temporaire .txt
    with tempfile.NamedTemporaryFile(
        suffix=".txt",
        delete=False,
        mode="w",
        encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        docs = TextLoader(tmp_path, encoding="utf-8").load()

        # Remplacer les métadonnées avec le titre fourni
        for doc in docs:
            doc.metadata["source"] = titre
            doc.metadata["titre"]  = titre

    finally:
        os.unlink(tmp_path)

    return docs




def load_documents(source: Union[str, Path, UploadedFile, dict]) -> list[Document]:
    """
    Point d'entrée unique — accepte :
      - un chemin string ou Path (fichier ou dossier)
      - un UploadedFile Django
    """
    if isinstance(source, dict):
        return load_from_dict(source)
    elif isinstance(source, UploadedFile):
        return load_from_upload(source)
    else:
        return load_from_path(source)