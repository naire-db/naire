from django import forms


class AttachmentForm(forms.Form):
    name = forms.CharField(max_length=200)
    file = forms.FileField(max_length=1000)
