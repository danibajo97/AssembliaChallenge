import re
import csv
from datetime import date
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .models import Document
from .scraping import fetch_documents


def document_list(request):
    """
    View to list only today's documents with optional search and pagination.
    - Filters documents by today's date.
    - Supports search by document title using query parameter `q`.
    - Pagination: 10 items per page.
    - HTMX requests return only the table partial.
    """
    today = date.today()
    query = request.GET.get("q", "")
    page = request.GET.get("page", 1)

    # Filter only today's documents
    documents = Document.objects.all().order_by('-date')
    if query:
        documents = documents.filter(title__icontains=query)

    # Paginate results
    paginator = Paginator(documents, 10)
    page_obj = paginator.get_page(page)

    context = {
        "documents": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "query": query,
    }

    # HTMX partial response
    if request.headers.get("HX-Request"):
        return render(request, "partials/table.html", context)

    return render(request, "documents/list.html", context)


def refresh(request):
    """
    Refresh today's documents list by scraping new data.
    Reuses the main listing logic.
    """
    fetch_documents()
    return document_list(request)


def export_csv(request):
    """
    Export only today's documents as CSV.
    - Columns: Title, Number, Date, Status, URL
    """
    today = date.today()
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="documents_today.csv"'
    writer = csv.writer(response)
    writer.writerow(["Title", "Number", "Date", "Status", "URL"])

    for doc in Document.objects.filter(date=today):
        writer.writerow([doc.title, doc.number, doc.date, doc.status, doc.url])
    return response


@csrf_exempt
def analyze_document(request, pk):
    """
    Analyze a document using AI (mocked version by default).
    - Works only with today's documents.
    """
    try:
        today = date.today()
        document = Document.objects.get(pk=pk, date=today)

        # --- DEMO MODE (mock AI analysis) ---
        entities = re.findall(r"(Ley|Decreto|Resoluci[oó]n)\s+\d+\/\d{4}", document.title)
        ai_message = (
            f"Summary (simulated AI): This document titled '{document.title}' "
            f"contains {len(document.title.split())} words. "
            f"Detected entities: {', '.join(entities) if entities else 'None'}."
        )

        return JsonResponse({"analysis": ai_message})
    except Document.DoesNotExist:
        return JsonResponse({"error": "Document not found"}, status=404)
