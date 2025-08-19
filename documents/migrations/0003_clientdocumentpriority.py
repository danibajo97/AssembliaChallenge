# Generated manually to avoid M2M field alteration issues

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_client"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientDocumentPriority",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("alta", "Alta"),
                            ("media", "Media"),
                            ("baja", "Baja"),
                        ],
                        default="media",
                        max_length=5,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "client",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documents.client",
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="documents.document",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("client", "document")},
            },
        ),
    ]