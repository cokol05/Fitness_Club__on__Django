from rest_framework import serializers
from .models import PersonalTraining

class PersonalTrainingSerializer(serializers.ModelSerializer):
    trainer_name = serializers.CharField(source='trainer.full_name', read_only=True)
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = PersonalTraining
        fields = ('id', 'trainer', 'trainer_name', 'client', 'client_name', 'date', 'start_time', 'end_time', 'status', 'is_available')


class PersonalTrainingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonalTraining
        fields = ('date', 'start_time', 'end_time')

    def validate(self, data):
        from datetime import date
        if data['date'] < date.today():
            raise serializers.ValidationError("Дата тренировки не может быть в прошлом")

        if data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("Время окончания должно быть позже времени начала")

        return data