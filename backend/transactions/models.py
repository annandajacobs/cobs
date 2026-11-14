from django.conf import settings
from django.db import models
from django.db.models import Q


class Transaction(models.Model):

    class Type(models.TextChoices):
        INCOME = "income", "Receita"
        EXPENSE = "expense", "Despesa"
        TRANSFER = "transfer", "Transferência"

    class Status(models.TextChoices):
        PAID = "paid", "Realizada"
        PENDING = "pending", "Pendente"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="transactions"
    )

    destination_account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        related_name="received_transfers",
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        related_name="transactions",
        null=True,
        blank=True
    )

    type = models.CharField(
        max_length=10,
        choices=Type.choices
    )

    description = models.CharField(max_length=200)

    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )

    transaction_date = models.DateTimeField()

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PAID
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="transaction_amount_must_be_positive"
            )
        ]

    def __str__(self):
        return f"{self.description} - R$ {self.amount}"

