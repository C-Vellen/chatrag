# Fonctions permettant de supprimer les fichiers media de MEDIAROOT :
# - si l'instance est supprimée (on_delete)
# - ou si le fichier FileField (ou ImageField) est modifié (on change)
# Fonctions appelées par les signaux définis dans les modules models.py des apps

import os

def auto_delete_file_on_delete(sender, instance):
    """ supprime le fichier de MEDIAROOT """
    for f in instance.get_file():
        if f:
            if os.path.isfile(f.path):
                os.remove(f.path)

def auto_delete_file_on_change(sender, instance):
    """ supprime les anciennes images de MEDIAROOT si elles sont mises à jour """

    if not instance.pk:
        return False
    
    for i, f in enumerate(instance.get_file()):
        try:
            old_file = sender.objects.get(pk=instance.pk).get_file()[i]
            if old_file and not old_file == f:
                try:
                    if os.path.isfile(old_file.path):
                        os.remove(old_file.path)
                except ValueError:
                    pass
        except sender.DoesNotExist:
            pass

