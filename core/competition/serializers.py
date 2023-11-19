from rest_framework import serializers
from .models import *
from datetime import datetime, timedelta

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class GenderSerialize(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'


class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = '__all__'


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class ResultsSerializer(serializers.ModelSerializer):
    competitor_detail = CompetitorSerializer(source='competitor', read_only=True)
    class Meta:
        model = Results
        fields = ['competitor','competitor_detail', 'competition', 'run1', 'run2']



    def validate(self, data):
        """
        Check that the competition and competitor combination is unique.
        """
        competition_id = data.get('competition')
        competitor_id = data.get('competitor')

        # Check if we're creating a new instance or updating an existing one
        if not self.instance:
            # This is a new instance, so we check if the combination already exists
            if Results.objects.filter(competition_id=competition_id, competitor_id=competitor_id).exists():
                raise serializers.ValidationError("A result for this competition and competitor already exists.")
        else:
            # This is an update, check if the combination exists elsewhere
            if Results.objects.exclude(pk=self.instance.pk).filter(competition_id=competition_id, competitor_id=competitor_id).exists():
                raise serializers.ValidationError("A result for this competition and competitor already exists with a different ID.")

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Add any additional fields you want to include in read operations

        ret['id'] = instance.id
        ret['place'] = instance.place
        ret['run_total'] = instance.run_total
        ret['point'] = instance.point
        ret['season_point'] = instance.season_point
        # You can add more fields if needed
        return ret

    def validate_time(self, time_str):
        # Split the string into its components
        minutes, seconds_centis = time_str.split(':')
        seconds, centiseconds = seconds_centis.split(',')
        # Construct a timedelta
        time_delta = timedelta(minutes=int(minutes), seconds=int(seconds), milliseconds=int(centiseconds) * 10)
        return time_delta

    def sum_times(self, run1, run2):
        # Validate and convert both run times to timedeltas
        run1_delta = self.validate_time(run1)
        run2_delta = self.validate_time(run2)
        # Sum the timedeltas
        run_total_delta = run1_delta + run2_delta
        # Extract the total time from the timedelta
        total_minutes = run_total_delta.seconds // 60
        total_seconds = run_total_delta.seconds % 60
        # Convert milliseconds to centiseconds
        total_centiseconds = run_total_delta.microseconds // 10000
        # Construct the run_total string
        run_total_str = f"{str(total_minutes).zfill(2)}:{str(total_seconds).zfill(2)},{str(total_centiseconds).zfill(2)}"
        return run_total_str

    def update(self, instance, validated_data):
        run1 = validated_data.get('run1', instance.run1)
        run2 = validated_data.get('run2')

        # Check if run2 is provided and is not None
        if run2 is not None:
            run_total = self.sum_times(run1, run2)
        else:
            run_total = run1

        validated_data['run_total'] = run_total

        # Now let the base class handle the actual update
        return super().update(instance, validated_data)
