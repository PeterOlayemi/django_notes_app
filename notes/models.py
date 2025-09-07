from django.db import models
from django.contrib.auth.models import User
import uuid
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from django.urls import reverse

# Create your models here.

class NoteTag(TaggedItemBase):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_object = models.ForeignKey(
        'Note',
        on_delete=models.CASCADE
    )

class Note(models.Model):
    FORMAT_CHOICES = [
        ("rich", "Rich Text"),
        ("markdown", "Markdown"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default="rich")
    file = models.FileField(upload_to='attachments/%Y/%m/', blank=True, null=True)

    is_pinned = models.BooleanField(default=False)
    is_trashed = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    lock_password = models.CharField(max_length=128, blank=True, null=True)

    tags = TaggableManager(through=NoteTag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('note_detail', args=[self.id])
    
    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return self.title
