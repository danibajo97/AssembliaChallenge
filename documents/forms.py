from django import forms

from documents.models import Client, ClientDocumentPriority, Document


class ClientForm(forms.ModelForm):
    """
    Form for creating and updating Client instances.
    """

    class Meta:
        model = Client
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ClientDocumentPriorityForm(forms.ModelForm):
    """
    Form for managing document priorities for clients
    """
    
    class Meta:
        model = ClientDocumentPriority
        fields = ['document', 'priority']
        widgets = {
            'document': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        client = kwargs.pop('client', None)
        super().__init__(*args, **kwargs)
        
        if client:
            # Show only documents not already assigned to this client
            assigned_docs = client.documents.all()
            self.fields['document'].queryset = Document.objects.exclude(
                id__in=assigned_docs.values_list('id', flat=True)
            )
