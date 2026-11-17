from rest_framework import serializers

from .models import Transaction
from categories.models import Category


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "destination_account",
            "category",
            "type",
            "description",
            "amount",
            "transaction_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        user = self.context["request"].user

        account = attrs.get(
            "account",
            self.instance.account if self.instance else None
        )

        destination = attrs.get(
            "destination_account",
            self.instance.destination_account if self.instance else None
        )

        category = attrs.get(
            "category",
            self.instance.category if self.instance else None
        )

        transaction_type = attrs.get(
            "type",
            self.instance.type if self.instance else None
        )

        if account and account.user != user:
            raise serializers.ValidationError({
                "account": "Esta conta não pertence ao usuário autenticado."
            })

        if account and not account.is_active:
            raise serializers.ValidationError({
                "account": "Não é possível utilizar uma conta inativa."
            })

        if transaction_type == Transaction.Type.TRANSFER:

            if not destination:
                raise serializers.ValidationError({
                    "destination_account": "Informe a conta de destino da transferência."
                })

            if destination.user != user:
                raise serializers.ValidationError({
                    "destination_account": "A conta de destino não pertence ao usuário autenticado."
                })

            if destination == account:
                raise serializers.ValidationError({
                    "destination_account": "A conta de destino deve ser diferente da conta de origem."
                })

            if not destination.is_active:
                raise serializers.ValidationError({
                    "destination_account": "A conta de destino está inativa."
                })

            if category:
                raise serializers.ValidationError({
                    "category": "Transferências não devem possuir categorias de receitas ou despesas."
                })

        else:
            if destination:
                raise serializers.ValidationError({
                    "destination_account": "Apenas transferências podem possuir conta de destino."
                })

        if category:
            if category.user != user:
                raise serializers.ValidationError({
                    "category": "Esta categoria não pertence ao usuário autenticado."
                })

            if not category.is_active:
                raise serializers.ValidationError({
                    "category": "Não é possível utilizar uma categoria inativa."
                })

            if transaction_type == Transaction.Type.INCOME:
                expected_type = Category.Type.INCOME

            elif transaction_type == Transaction.Type.EXPENSE:
                expected_type = Category.Type.EXPENSE

            else:
                expected_type = None

            if category.type != expected_type:
                raise serializers.ValidationError({
                    "category": "A categoria não corresponde ao tipo da movimentação."
                })

        return attrs
