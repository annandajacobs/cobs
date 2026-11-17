from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


User = get_user_model()


class TransactionAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="annanda",
            email="annanda@example.com",
            password="senha123"
        )

        self.other_user = User.objects.create_user(
            username="outro_usuario",
            email="outro@example.com",
            password="senha123"
        )

        self.account = Account.objects.create(
            user=self.user,
            name="Conta corrente",
            type=Account.Type.CHECKING
        )

        self.destination_account = Account.objects.create(
            user=self.user,
            name="Poupança",
            type=Account.Type.SAVINGS
        )

        self.other_account = Account.objects.create(
            user=self.other_user,
            name="Conta de outro usuário",
            type=Account.Type.CHECKING
        )

        self.income_category = Category.objects.create(
            user=self.user,
            name="Salário",
            type=Category.Type.INCOME
        )

        self.expense_category = Category.objects.create(
            user=self.user,
            name="Alimetação",
            type=Category.Type.EXPENSE
        )

        self.client.force_authenticate(user=self.user)

        self.list_url = reverse("transaction-list-create")

    def test_create_income(self):
        """Deve permitir cadastrar uma receita válida."""

        data = {
            "account": self.account.id,
            "category": self.income_category.id,
            "type": "income",
            "description": "salário",
            "amount": "300.00",
            "transaction_date": timezone.now().isoformat(),
            "status": "paid"
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_create_expense_with_income_category(self):
        """Não deve permitir despesa com categoria de receita"""

        data = {
            "account": self.account.id,
            "category": self.income_category.id,
            "type": "expense",
            "description": "Compra para supermercado",
            "amount": "150.00",
            "transaction_date": timezone.now().isoformat(),
            "status": "paid"
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_create_transfer_without_destination(self):
        """Não deve permitir transferência sem conta de destino."""

        data = {
            "account": self.account.id,
            "type": "transfer",
            "description": "Transferência",
            "amount": "500.00",
            "transaction_date": timezone.now().isoformat(),
            "status": "paid"
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_create_transfer_successfully(self):
        """Deve permitir transferência entre contas do mesmo usuário."""

        data = {
            "account": self.account.id,
            "destination_account": self.destination_account.id,
            "type": "transfer",
            "description": "Transferência para poupança",
            "amount": "500.00",
            "transaction_date": timezone.now().isoformat(),
            "status": "paid"
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_create_transaction_using_another_users_account(self):
        """Não deve permitir utilizar conta de outro usuário."""

        data = {
            "account": self.other_account.id,
            "category": self.expense_category.id,
            "type": "expense",
            "description": "Despesa indevida",
            "amount": "100.00",
            "transaction_date": timezone.now().isoformat(),
            "status": "paid"
        }

        response = self.client.post(
            self.list_url,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Transaction.objects.count(), 0)

    def test_list_only_authenticated_users_transactions(self):
        """Deve listar somente as movimentações do usuário autenticado."""

        Transaction.objects.create(
            user=self.user,
            account=self.account,
            category=self.expense_category,
            type=Transaction.Type.EXPENSE,
            description="Minha despesa",
            amount="100.00",
            transaction_date=timezone.now()
        )

        Transaction.objects.create(
            user=self.other_user,
            account=self.other_account,
            type=Transaction.Type.EXPENSE,
            description="Despesa de outro usuário",
            amount="200.00",
            transaction_date=timezone.now()
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["description"],
            "Minha despesa"
        )