from django import forms
from .models import Note
from taggit.models import Tag
from django.contrib.auth.hashers import make_password

class NoteForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Separate multiple tags with commas."
    )

    class Meta:
        model = Note
        fields = ["title", "format", "body", "file", "is_locked", "lock_password", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "format": forms.Select(attrs={"class": "form-control", "required": True}),
            "body": forms.Textarea(attrs={"class": "form-control", "required": True}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_locked": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "lock_password": forms.PasswordInput(attrs={"class": "form-control"}),
            "tags": forms.TextInput(attrs={"class": "form-control", "placeholder": "comma,separated"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(tag.name for tag in self.instance.tags.all())

    def clean(self):
        cleaned_data = super().clean()
        is_locked = cleaned_data.get("is_locked")
        lock_password = cleaned_data.get("lock_password")

        if is_locked and not lock_password:
            raise forms.ValidationError("Lock password is required when locking a note.")

        if is_locked and lock_password:
            cleaned_data["lock_password"] = make_password(lock_password)

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            tag_names = [t.strip() for t in self.cleaned_data["tags"].split(",") if t.strip()]
            instance.tags.set([Tag.objects.get_or_create(name=name)[0] for name in tag_names])
        return instance
