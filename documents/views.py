import re
import csv
from datetime import date

from django.db import models
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, UpdateView
from rest_framework.reverse import reverse_lazy

from .forms import ClientForm
from .models import Document, Client, ClientDocumentPriority
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


class ClientView(ListView):
    model = Client
    template_name = "client/list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Client.objects.filter(customer=self.request.user).annotate(count_docu=models.Count("documents"))


class ClientDocumentsView(DetailView):
    model = Client
    template_name = "client/documents.html"
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get documents with their priorities
        priorities = ClientDocumentPriority.objects.filter(client=self.object).select_related('document')
        context["document_priorities"] = priorities
        return context


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "client/form.html"
    context_object_name = "client"
    success_url = reverse_lazy("documents:client_list")


class ClientDocumentPriorityView(ListView):
    model = ClientDocumentPriority
    template_name = "client/priority_list.html"
    context_object_name = "priorities"
    paginate_by = 10

    def get_queryset(self):
        queryset = ClientDocumentPriority.objects.filter(
            client__customer=self.request.user
        ).select_related('client', 'document').order_by('-created_at')
        
        # Filter by priority if specified
        priority_filter = self.request.GET.get('priority')
        if priority_filter and priority_filter in ['alta', 'media', 'baja']:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by client if specified
        client_filter = self.request.GET.get('client')
        if client_filter:
            try:
                client_id = int(client_filter)
                queryset = queryset.filter(client_id=client_id)
            except (ValueError, TypeError):
                pass
        
        # Search by document title
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(document__title__icontains=search_query)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get priority summary for the user's clients
        user_priorities = ClientDocumentPriority.objects.filter(
            client__customer=self.request.user
        ).values('priority').annotate(count=models.Count('priority'))
        context['priority_summary'] = {item['priority']: item['count'] for item in user_priorities}
        
        # Get user's clients for filter dropdown
        context['user_clients'] = Client.objects.filter(customer=self.request.user)
        
        # Current filter values
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_client'] = self.request.GET.get('client', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context


@csrf_exempt
def update_document_priority(request, client_id, document_id):
    """
    HTMX/AJAX view to update document priority for a specific client
    """
    if request.method == 'POST':
        try:
            priority = request.POST.get('priority')
            if priority not in ['alta', 'media', 'baja']:
                if request.headers.get('HX-Request'):
                    return HttpResponse('<div class="text-red-600">Prioridad inválida</div>', status=400)
                return JsonResponse({'error': 'Prioridad inválida'}, status=400)
            
            client = Client.objects.get(id=client_id, customer=request.user)
            document = Document.objects.get(id=document_id)
            
            # Create or update priority
            priority_obj, created = ClientDocumentPriority.objects.update_or_create(
                client=client,
                document=document,
                defaults={'priority': priority}
            )
            
            # HTMX request - return partial template
            if request.headers.get('HX-Request'):
                # Get updated priorities list for the partial
                priorities = ClientDocumentPriority.objects.filter(
                    client__customer=request.user
                ).select_related('client', 'document').order_by('-created_at')
                
                # Apply current filters if any
                priority_filter = request.GET.get('priority')
                if priority_filter and priority_filter in ['alta', 'media', 'baja']:
                    priorities = priorities.filter(priority=priority_filter)
                
                client_filter = request.GET.get('client')
                if client_filter:
                    try:
                        client_id_filter = int(client_filter)
                        priorities = priorities.filter(client_id=client_id_filter)
                    except (ValueError, TypeError):
                        pass
                
                search_query = request.GET.get('search')
                if search_query:
                    priorities = priorities.filter(document__title__icontains=search_query)
                
                return render(request, 'partials/priority_table.html', {'priorities': priorities})
            
            # Regular AJAX request
            return JsonResponse({
                'success': True,
                'priority': priority_obj.get_priority_display(),
                'created': created
            })
            
        except (Client.DoesNotExist, Document.DoesNotExist):
            if request.headers.get('HX-Request'):
                return HttpResponse('<div class="text-red-600">Cliente o documento no encontrado</div>', status=404)
            return JsonResponse({'error': 'Cliente o documento no encontrado'}, status=404)
        except Exception as e:
            if request.headers.get('HX-Request'):
                return HttpResponse(f'<div class="text-red-600">Error: {str(e)}</div>', status=500)
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt
def delete_document_priority(request, client_id, document_id):
    """
    HTMX/AJAX view to delete document priority for a specific client
    """
    if request.method == 'DELETE':
        try:
            client = Client.objects.get(id=client_id, customer=request.user)
            document = Document.objects.get(id=document_id)
            
            priority_obj = ClientDocumentPriority.objects.get(
                client=client,
                document=document
            )
            priority_obj.delete()
            
            # HTMX request - return updated partial template
            if request.headers.get('HX-Request'):
                # Get updated priorities list for the partial
                priorities = ClientDocumentPriority.objects.filter(
                    client__customer=request.user
                ).select_related('client', 'document').order_by('-created_at')
                
                # Apply current filters if any (same logic as update)
                priority_filter = request.GET.get('priority')
                if priority_filter and priority_filter in ['alta', 'media', 'baja']:
                    priorities = priorities.filter(priority=priority_filter)
                
                client_filter = request.GET.get('client')
                if client_filter:
                    try:
                        client_id_filter = int(client_filter)
                        priorities = priorities.filter(client_id=client_id_filter)
                    except (ValueError, TypeError):
                        pass
                
                search_query = request.GET.get('search')
                if search_query:
                    priorities = priorities.filter(document__title__icontains=search_query)
                
                return render(request, 'partials/priority_table.html', {'priorities': priorities})
            
            # Regular AJAX request
            return JsonResponse({'success': True})
            
        except (Client.DoesNotExist, Document.DoesNotExist):
            if request.headers.get('HX-Request'):
                return HttpResponse('<div class="text-red-600">Cliente o documento no encontrado</div>', status=404)
            return JsonResponse({'error': 'Cliente o documento no encontrado'}, status=404)
        except ClientDocumentPriority.DoesNotExist:
            if request.headers.get('HX-Request'):
                return HttpResponse('<div class="text-red-600">Prioridad no encontrada</div>', status=404)
            return JsonResponse({'error': 'Prioridad no encontrada'}, status=404)
        except Exception as e:
            if request.headers.get('HX-Request'):
                return HttpResponse(f'<div class="text-red-600">Error: {str(e)}</div>', status=500)
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def assign_documents_to_client(request, client_id):
    """
    View to assign documents to a client with priorities
    """
    try:
        client = Client.objects.get(id=client_id, customer=request.user)
    except Client.DoesNotExist:
        return render(request, '404.html', status=404)
    
    if request.method == 'POST':
        document_ids = request.POST.getlist('documents')
        priority = request.POST.get('priority', 'media')
        
        if priority not in ['alta', 'media', 'baja']:
            priority = 'media'
        
        success_count = 0
        for doc_id in document_ids:
            try:
                document = Document.objects.get(id=doc_id)
                _, created = ClientDocumentPriority.objects.update_or_create(
                    client=client,
                    document=document,
                    defaults={'priority': priority}
                )
                if created:
                    success_count += 1
            except Document.DoesNotExist:
                continue
        
        if request.headers.get('HX-Request'):
            return JsonResponse({
                'success': True,
                'message': f'{success_count} documentos asignados correctamente'
            })
        
        return redirect('documents:client_documents', pk=client.id)
    
    # GET request - show available documents
    assigned_docs = ClientDocumentPriority.objects.filter(client=client).values_list('document_id', flat=True)
    available_documents = Document.objects.exclude(id__in=assigned_docs).order_by('-date')[:50]
    
    context = {
        'client': client,
        'available_documents': available_documents,
        'priority_choices': ClientDocumentPriority.PRIORITY_CHOICES,
    }
    
    return render(request, 'client/assign_documents.html', context)
