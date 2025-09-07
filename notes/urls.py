from django.urls import path

from .views import *

urlpatterns = [
    path("search-suggestions/", search_suggestions, name="search_suggestions"),
    path("", HomeView.as_view(), name="home"),
    path("notes/new/", NoteCreateView.as_view(), name="note_create"),
    path("notes/<uuid:pk>/", NoteDetailView.as_view(), name="note_detail"),
    path("notes/<uuid:note_id>/trash/", trash_note, name="note_trash"),
    path("notes/<uuid:note_id>/pin/", pin_note, name="pin_note"),
    path("notes/<uuid:note_id>/unpin/", unpin_note, name="unpin_note"),
    path("notes/<uuid:pk>/export/", note_export, name="note_export"),
    path("trash/", TrashedNotesView.as_view(), name="trashed_notes"),
    path("trash/empty/", empty_trash, name="empty_trash"),
    path("notes/<uuid:note_id>/restore/", restore_note, name="note_restore"),
    path("notes/<uuid:note_id>/delete/", delete_note_permanently, name="note_delete"),
    path("archive/", ArchivedNotesView.as_view(), name="archived_notes"),
    path("notes/<uuid:note_id>/archive/", archive_note, name="note_archive"),
    path("notes/<uuid:note_id>/unarchive/", unarchive_note, name="note_unarchive"),
    path('analytics/', analytics_view, name='analytics'),
]
