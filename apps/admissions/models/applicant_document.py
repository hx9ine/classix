from django.db import models

from apps.core.models import BaseModel

from .applicant import Applicant


class ApplicantDocument(BaseModel):
    """
    Documents uploaded for an applicant.
    """

    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    doc_type = models.CharField(
        max_length=100,
    )

    file_url = models.CharField(
        max_length=500,
    )

    class Meta:
        db_table = "applicant_document"

        ordering = [
            "doc_type",
        ]

    def __str__(self):
        return self.doc_type