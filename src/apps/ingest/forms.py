from django import forms


class DocumentForm(forms.Form):
    file = forms.FileField(
        label="Fichier :",
        widget=forms.FileInput(attrs={"class": "file-input  "}),
        required=False
    )
    uri = forms.CharField(
        label="URL   ",
        widget=forms.TextInput(attrs={
            "class": "h-9 p-0 px-2 rounded text-xs bg-slate-200",
            "style": "margin-top:4px",
            "placeholder": "lien url, youtube...",
            }),
        required=False
    )
