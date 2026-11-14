from django.conf import settings
from django.db import models


class Category(models.Model):

    class Type(models.TextChoices):
        INCOME = "income", "Receita"
        EXPENSE = "expense", "Despesa"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    name = models.CharField(max_length=80)
    type = models.CharField(
        max_length=10,
        choices=Type.choices
    )

    color = models.CharField(max_length=7, default="#64748b")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "type"],
                name="unique_category_per_user"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

