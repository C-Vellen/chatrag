from django import forms


class DocumentForm(forms.Form):
    file = forms.FileField(
        label="Fichier :",
        widget=forms.FileInput(attrs={
            "class": (
                "text-xs text-gray-500 "
                "file:mr-4 file:py-1 file:px-2 "
                "file:rounded file:border file:border-gray-300 "
                "file:text-xs "
                "file:bg-gray-50 file:text-gray-700 "
                "hover:file:bg-gray-100 file:cursor-pointer"
                )
            }),
        required=False
    )
    uri = forms.CharField(
        label="URL :  ",
        widget=forms.TextInput(attrs={
            "class": (
                "text-xs text-gray-500 "
                "w-80 mr-4 py-1 px-2 "
                "rounded border border-gray-300 "
                "bg-gray-50 text-gray-700 "
                "hover:bg-gray-100 cursor-pointer"
                
                
                
            ),
            "placeholder": "https://youtube.com/... ou src/documents/..."
            }),
        required=False
    )
