from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label="Fichier .txt, .md ou .pdf ",
        widget=forms.FileInput(attrs={"class": "file-input"}),
    )
    
class UploadDirForm(forms.Form):
    path = forms.CharField(
        label="Chemin de dossier de fichiers:",
        widget=forms.TextInput(attrs={"class": "h-9 m-0 p-0 px-2 rounded text-xs bg-slate-200", "value":"src/documents"}),
    )

class UploadVideoForm(forms.Form):
    url = forms.URLField(
        label="Video Youtube\t\t ",
        widget=forms.URLInput(attrs={"class": "h-9 m-0 p-0 px-2 rounded text-xs bg-slate-200", "placeholder":"https://www.youtube.com/watch?v=..."}),
    )