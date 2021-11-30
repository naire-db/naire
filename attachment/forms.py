from django import forms
from .models import Attachment, Image


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ('file',)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)
