from rest_framework import serializers

from logs.models import DashboardLog


class DashboardLogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = DashboardLog

    def create(self, validated_data):
        user = self.context['request'].user  
        log = self.Meta.model.objects.create(
            user=user, **validated_data
        )
        return log