from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="list"),
    path("refresh/", views.refresh, name="refresh"),
    path("export/", views.export_csv, name="export_csv"),
    path("analyze/<int:pk>/", views.analyze_document, name="analyze_document"),
]
