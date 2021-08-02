from rest_framework import serializers

from accounts.models import Account


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['account_number', 'name']
        # fields = ['account_number', 'name', 'balance', 'balance_currency']
        # fields = '__all__'