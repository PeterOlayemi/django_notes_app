from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q, F
from django.db.models.functions import TruncMonth, TruncDay
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, View
from datetime import timedelta
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph
import json
import markdown2

from .models import *
from .forms import *

# Create your views here.

@login_required
def search_suggestions(request):
    q = request.GET.get("q", "").strip()
    data = {
        "notes": []
    }

    if q:
        notes = Note.objects.filter(
            Q(title__icontains=q) |
            Q(tags__name__icontains=q),
            user=request.user
        ).distinct()[:5]
        data["notes"] = [
            {"title": n.title, "url": n.get_absolute_url()} for n in notes
        ]

    return JsonResponse(data)

class HomeView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "notes/home.html"
    context_object_name = "notes"

    def get_queryset(self):
        return (
            Note.objects.filter(user=self.request.user, is_trashed=False, is_archived=False)
            .select_related("user")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_notes = self.get_queryset()

        context["pinned_notes"] = all_notes.filter(is_pinned=True).order_by("-updated_at")

        other_notes = all_notes.filter(is_pinned=False).order_by("-updated_at")
        paginator = Paginator(other_notes, 6)
        page = self.request.GET.get('page')
        other_notes = paginator.get_page(page)

        context["other_notes"] = other_notes
        context["form"] = NoteForm()

        return context

class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    form_class = NoteForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse("home")

class NoteDetailView(LoginRequiredMixin, View):
    template_name = "notes/note_detail.html"

    def get(self, request, pk):
        note = Note.objects.get(pk=pk, user=request.user)

        unlocked_notes = request.session.get("unlocked_notes", {})

        if isinstance(unlocked_notes, list):
            unlocked_notes = {}

        now = timezone.now()
        cleaned = {}
        for note_id, unlock_info in unlocked_notes.items():
            try:
                expiry = timezone.datetime.fromisoformat(unlock_info["expiry"])
                if now <= expiry:
                    cleaned[note_id] = unlock_info
            except Exception:
                continue

        request.session["unlocked_notes"] = cleaned
        unlocked_notes = cleaned

        if note.is_locked:
            unlock_info = unlocked_notes.get(str(pk))
            if not unlock_info:
                return render(request, "notes/note_password.html", {"note": note})

        content = note.body
        if note.format == "markdown":
            content = markdown2.markdown(note.body or "")

        form = NoteForm(instance=note)

        return render(
            request,
            self.template_name,
            {"note": note, "content": content, "form": form},
        )

    def post(self, request, pk):
        note = get_object_or_404(Note, pk=pk, user=request.user)
        submit_type = request.POST.get("submit_type")

        if submit_type == "unlock":
            password = request.POST.get("lock_password")
            if check_password(password, note.lock_password):
                unlocked_notes = request.session.get("unlocked_notes", {})

                if isinstance(unlocked_notes, list):
                    unlocked_notes = {}

                now = timezone.now()
                cleaned = {}
                for note_id, unlock_info in unlocked_notes.items():
                    try:
                        expiry = timezone.datetime.fromisoformat(unlock_info["expiry"])
                        if now <= expiry:
                            cleaned[note_id] = unlock_info
                    except Exception:
                        continue

                cleaned[str(pk)] = {"expiry": (now + timedelta(minutes=1)).isoformat()}
                request.session["unlocked_notes"] = cleaned

                return redirect("note_detail", pk=pk)

            return render(
                request,
                "notes/note_password.html",
                {"note": note, "error": "Incorrect password. Try again."},
            )

        elif submit_type == "edit":
            form = NoteForm(request.POST, request.FILES, instance=note)
            if form.is_valid():
                note = form.save(commit=False)
                note.save()
                return redirect("note_detail", pk=pk)

            content = note.body
            if note.format == "markdown":
                content = markdown2.markdown(note.body or "")

            return render(request, self.template_name, {
                "note": note,
                "content": content,
                "form": form,
            })
    
@login_required
def trash_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_trashed = True
    note.save()
    messages.success(request, f"Note '{note.title}' moved to Trash.")
    return redirect("home")

@login_required
def pin_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_pinned = True
    note.save()
    messages.success(request, f"'{note.title}' has been pinned.")
    return redirect("home")

@login_required
def unpin_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_pinned = False
    note.save()
    messages.info(request, f"'{note.title}' has been unpinned.")
    return redirect("home")

@login_required
def note_export(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)

    export_format = request.GET.get("format", "txt")

    if export_format == "txt":
        filename = f"{slugify(note.title)}.txt"
        content = strip_tags(note.body) if note.format == "rich" else note.body
        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    elif export_format == "md":
        filename = f"{slugify(note.title)}.md"
        response = HttpResponse(note.body, content_type="text/markdown")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    elif export_format == "html":
        filename = f"{slugify(note.title)}.html"
        html_content = f"<html><head><meta charset='utf-8'></head><body><h1>{note.title}</h1>{note.body}</body></html>"
        response = HttpResponse(html_content, content_type="text/html")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    elif export_format == "pdf":
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = [Paragraph(note.title, styles["Title"]),
                 Paragraph(note.body, styles["Normal"])]
        doc.build(story)

        filename = f"{slugify(note.title)}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        buffer.close()
        return response

    else:
        return HttpResponse("Unsupported export format", status=400)

class TrashedNotesView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "notes/trashed_notes.html"
    context_object_name = "notes"

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_trashed=True).order_by("-updated_at")
    
@login_required
@require_POST
def empty_trash(request):
    trashed_notes = Note.objects.filter(user=request.user, is_trashed=True)
    count = trashed_notes.count()
    trashed_notes.delete()
    messages.success(request, f"{count} note(s) permanently deleted from Trash.")
    return redirect("trashed_notes")

@login_required
@require_POST
def restore_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user, is_trashed=True)
    note.is_trashed = False
    note.save()
    messages.success(request, f"Note '{note.title}' has been restored.")
    return redirect("trashed_notes")

@login_required
@require_POST
def delete_note_permanently(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user, is_trashed=True)
    title = note.title
    note.delete()
    messages.success(request, f"Note '{title}' permanently deleted.")
    return redirect("trashed_notes")

class ArchivedNotesView(LoginRequiredMixin, ListView):
    model = Note
    template_name = "notes/archived_notes.html"
    context_object_name = "notes"

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user, is_archived=True, is_trashed=False).order_by("-updated_at")

@login_required
def archive_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_archived = True
    note.save()
    messages.success(request, f"Note '{note.title}' moved to Archive.")
    return redirect("note_detail", pk=note_id)

@login_required
def unarchive_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    note.is_archived = False
    note.save()
    messages.success(request, f"Note '{note.title}' removed from Archive.")
    return redirect("archived_notes")

@login_required
def analytics_view(request):
    user = request.user

    notes_per_month = (
        Note.objects.filter(user=user)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    notes_per_tag = (
        Note.objects.filter(user=user)
        .values('tags__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    notes_per_day = (
        Note.objects.filter(user=user, created_at__gte=timezone.now()-timezone.timedelta(days=30))
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    top_tags = notes_per_tag[:10]

    with_attachments = Note.objects.filter(user=user).exclude(file='').count()
    without_attachments = Note.objects.filter(user=user, file='').count()

    avg_length = (
        Note.objects.filter(user=user)
        .annotate(length=F('body'))
        .aggregate(avg=Count('length'))
    )

    archived = Note.objects.filter(user=user, is_archived=True).count()
    active = Note.objects.filter(user=user, is_archived=False).count()

    tag_diversity = (
        Note.objects.filter(user=user)
        .annotate(num_tags=Count('tags'))
        .aggregate(avg=Count('num_tags'))
    )

    context = {
        "notes_per_month": json.dumps(list(notes_per_month), cls=DjangoJSONEncoder),
        "notes_per_tag": json.dumps(list(notes_per_tag), cls=DjangoJSONEncoder),
        "notes_per_day": json.dumps(list(notes_per_day), cls=DjangoJSONEncoder),
        "top_tags": list(top_tags),
        "with_attachments": with_attachments,
        "without_attachments": without_attachments,
        "avg_length": avg_length,
        "archived": archived,
        "active": active,
        "tag_diversity": tag_diversity,
        "has_notes": Note.objects.filter(user=user).exists(),
        "has_tags": notes_per_tag.exists(),
    }
    return render(request, "notes/analytics.html", context)
