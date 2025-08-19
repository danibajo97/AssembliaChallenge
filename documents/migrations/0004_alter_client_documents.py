# Generated manually to alter M2M field with through

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0003_clientdocumentpriority"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="client",
            name="documents",
        ),
        migrations.AddField(
            model_name="client",
            name="documents",
            field=models.ManyToManyField(
                blank=True,
                through="documents.ClientDocumentPriority",
                to="documents.document",
            ),
        ),
    ]