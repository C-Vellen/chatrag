from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)
from langchain_core.documents import Document

def load_documents(source: str | Path) -> list[Document]:
    """
    Charge des documents depuis un fichier ou un dossier.
    Supporte : .pdf, .txt, .md
    """
    source = Path(source)
    # si source = dossier unique
    if source.is_dir():
        loaders = [
            DirectoryLoader(str(source), glob="**/*.pdf", loader_cls=PyPDFLoader),
            DirectoryLoader(str(source), glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(str(source), glob="**/*.md",  loader_cls=TextLoader),
        ]
        docs = []
        for loader in loaders:
            for docu in loader.load():
                print("\t> Fichier: ", docu.metadata["source"].split('/')[-1])
            docs.extend(loader.load())
        return docs

    # si source = fichier unique
    suffix = source.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(source)).load()
    elif suffix in (".txt", ".md"):
        return TextLoader(str(source)).load()
    else:
        raise ValueError(f"Format non supporté : {suffix}")