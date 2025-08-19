from django.contrib.auth.models import User
from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=255)
    number = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=100)
    url = models.URLField()

    class Meta:
        unique_together = ("number", "date")

    def __str__(self):
        return f"{self.number} - {self.title}"


class ClientDocumentPriority(models.Model):
    PRIORITY_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    priority = models.CharField(max_length=5, choices=PRIORITY_CHOICES, default='media')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('client', 'document')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.client.name} - {self.document.title} ({self.get_priority_display()})"


class Client(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    documents = models.ManyToManyField(Document, through='ClientDocumentPriority', blank=True)

    def __str__(self):
        return self.name
