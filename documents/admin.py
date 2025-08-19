from django.contrib import admin

from documents.models import Client, Document, ClientDocumentPriority


class ClientDocumentPriorityInline(admin.TabularInline):
    model = ClientDocumentPriority
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer']
    inlines = [ClientDocumentPriorityInline]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'number', 'date', 'status']
    list_filter = ['date', 'status']
    search_fields = ['title', 'number']


@admin.register(ClientDocumentPriority)
class ClientDocumentPriorityAdmin(admin.ModelAdmin):
    list_display = ['client', 'document', 'priority', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = ['client__name', 'document__title']
