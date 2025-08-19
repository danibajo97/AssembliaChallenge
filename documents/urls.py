from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="list"),
    path("refresh/", views.refresh, name="refresh"),
    path("export/", views.export_csv, name="export_csv"),
    path("analyze/<int:pk>/", views.analyze_document, name="analyze_document"),

    path("clients/", views.ClientView.as_view(), name="client_list"),
    path("clients/<int:pk>/", views.ClientDocumentsView.as_view(), name="client_documents"),
    path("clients_update/<int:pk>/", views.ClientUpdateView.as_view(), name="client_update"),
    
    # Priority management URLs
    path("priorities/", views.ClientDocumentPriorityView.as_view(), name="priority_list"),
    path("priority/update/<int:client_id>/<int:document_id>/", 
         views.update_document_priority, name="update_priority"),
    path("priority/delete/<int:client_id>/<int:document_id>/", 
         views.delete_document_priority, name="delete_priority"),
    path("clients/<int:client_id>/assign-documents/", 
         views.assign_documents_to_client, name="assign_documents"),
]
