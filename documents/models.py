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
