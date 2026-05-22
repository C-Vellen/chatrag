from django import forms


class DocumentForm(forms.Form):
    file = forms.FileField(
        label="Fichier .txt, .md ou .pdf ",
        widget=forms.FileInput(attrs={"class": "file-input"}),
        required=False
    )
    uri = forms.CharField(
        label="URI: chemin dossier ou url video youtube ",
        widget=forms.TextInput(attrs={"class": "h-9 m-0 p-0 px-2 rounded text-xs bg-slate-200"}),
        required=False
    )
