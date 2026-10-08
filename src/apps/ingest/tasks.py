import logging
from celery import shared_task
from .models import DocumentRef
from .services.ingest import ingest

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def ingest_documents_task(self, docIdList: list) -> dict:
    """
    Tâche Celery qui ingère une liste de documents.

    bind=True : donne accès à `self` (l'instance de la tâche),
    ce qui permet de mettre à jour l'état (self.update_state)
    pendant l'exécution.

    docIdList : liste d'UUIDs des documents à ingérer
    """
    results = {}   # stocke le résultat doc par doc
    print("IN ingest_documents_task")
    for i, docId in enumerate(docIdList):
        try:
            doc = DocumentRef.objects.get(id=docId)
            
            print(doc.titre)

            # update_state : met à jour l'état de la tâche dans Redis.
            # Le JS pourra interroger cet état via l'endpoint /ingest/status/
            # 'PROGRESS' est un état personnalisé (au-delà de PENDING/SUCCESS/FAILURE)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i,           # index du doc en cours
                    'total':   len(docIdList),
                    'docId':   str(docId),
                    'titre':   doc.titre,
                    'status':  'running',
                    'results': results,     # résultats des docs déjà traités
                }
            )
            print(f"Ingestion de '{doc.titre}' ({i+1}/{len(docIdList)})")

            logger.info(f"Ingestion de '{doc.titre}' ({i+1}/{len(docIdList)})")

            ingest(doc)

            results[str(docId)] = {
                'titre':  doc.titre,
                'status': 'done',
            }
            logger.info(f"'{doc.titre}' ingéré avec succès")

        except DocumentRef.DoesNotExist:
            results[str(docId)] = {
                'titre':  str(docId),
                'status': 'error',
                'error':  'Document introuvable',
            }
            logger.error(f"Document {docId} introuvable")

        except Exception as e:
            # L'exception est catchée → le pipeline continue avec les autres docs
            # (sans ça, une erreur sur un doc stopperait tous les suivants)
            results[str(docId)] = {
                'titre':  doc.titre if doc else str(docId),
                'status': 'error',
                'error':  str(e),
            }
            logger.error(f"Erreur ingestion {docId} : {e}", exc_info=True)

    # Retour final stocké dans Redis — accessible via task.result
    return {
        'status':  'done',
        'total':   len(docIdList),
        'results': results,
    }