from rest_framework import serializers
from .models import *
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class GenderSerialize(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'


class CompetitorSerializer(serializers.ModelSerializer):
    # Use distinct names for write-only and read-only representations
    gender_id = serializers.PrimaryKeyRelatedField(
        queryset=Gender.objects.all(), 
        source='gender', 
        write_only=True
    )
    school_id = serializers.PrimaryKeyRelatedField(
        queryset=School.objects.all(), 
        source='school', 
        write_only=True
    )
    gender = serializers.CharField(source='gender.gender', read_only=True)
    school = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = Competitor
        fields = ['id', 'gender_id', 'name', 'surname', 'school_id', 'year', 'gender', 'school']


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id','season','created']


class DisciplineSerializer(serializers.ModelSerializer):
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True,
    )

    # For read operations (GET)
    season = SeasonSerializer(read_only=True)

    class Meta:
        model = Discipline
        fields = ['id', 'discipline', 'season_id', 'season']


class StageSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer(read_only=True)  # Nested StageSerializer
    class Meta:
        model = Stage
        fields = ['id', 'discipline', 'period', 'name']


class GroupSerializer(serializers.ModelSerializer):
    stage = StageSerializer(read_only=True)  # Nested StageSerializer


    class Meta:
        model = Group
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = '__all__'

    def validate(self, data):
        """
        Check that the competition and competitor combination is unique.
        """
        group_id = data.get('group')
        competitor_id = data.get('competitor')

        # Check if we're creating a new instance or updating an existing one
        if not self.instance:
            # This is a new instance, so we check if the combination already exists
            if Cart.objects.filter(group_id=group_id, competitor_id=competitor_id).exists():
                raise serializers.ValidationError("A result for this group and competitor already exists.")
        else:
            # This is an update, check if the combination exists elsewhere
            if Cart.objects.exclude(pk=self.instance.pk).filter(group_id=group_id, competitor_id=competitor_id).exists():
                raise serializers.ValidationError("A result for this group and competitor already exists with a different ID.")

        return data


class ResultsSerializer(serializers.ModelSerializer):
    cart_detail = CartSerializer(source='competitor', read_only=True)
    status = serializers.CharField(source='status.status', read_only=True)

    class Meta:
        model = Results
        fields = '__all__'



    def validate(self, data):
        """
        Check that the competition and competitor combination is unique.
        """
        competitor_id = data.get('competitor')

        # Check if we're creating a new instance or updating an existing one
        if not self.instance:
            # This is a new instance, so we check if the combination already exists
            if Results.objects.filter(competitor_id=competitor_id).exists():
                raise serializers.ValidationError("A result for this competitor already exists.")
        else:
            # This is an update, check if the combination exists elsewhere
            if Results.objects.exclude(pk=self.instance.pk).filter(competitor_id=competitor_id).exists():
                raise serializers.ValidationError("A result for this competitor already exists with a different ID.")

        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)

        competitor_serializer = CompetitorSerializer(instance.competitor.competitor)
        response['competitor'] = competitor_serializer.data



        # Include other fields from Results model
        response['id'] = instance.id
        response['place'] = instance.place
        response['run1'] = instance.run1
        response['run2'] = instance.run2
        response['run_total'] = instance.run_total
        response['point'] = instance.point
        response['season_point'] = instance.season_point

        return response

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
        # Assuming run1 and run2 are provided in the correct format 'mm:ss,00'
        run1 = validated_data.get('run1', instance.run1)
        run2 = validated_data.get('run2', instance.run2)

        # Check if both runs are provided
        if run1 and run2:
            # Calculate run_total
            run_total = self.sum_times(run1, run2)
            validated_data['run_total'] = run_total
        elif run1:
            validated_data['run_total'] = run1
        elif run2:
            validated_data['run_total'] = run2

        # Now let the base class handle the actual update
        instance = super().update(instance, validated_data)

        # After updating, recalculate the placements
        self.recalculate_placements(instance)

        return instance

    def recalculate_placements(self, instance):
        # Get all the results in the same group as the current instance
        group_results = Results.objects.filter(
            competitor__group=instance.competitor.group,
            run_total__isnull=False
        ).exclude(
            id=instance.id  # Exclude the current instance
        )

        # Add the current instance to the list and sort by run_total
        all_results = list(group_results) + [instance]
        all_results.sort(key=lambda x: self.validate_time(x.run_total))

        # Update the placement
        for idx, result in enumerate(all_results, 1):
            result.place = idx
            result.save(update_fields=['place'])



class RandomizeBibNumbersSerializer(serializers.Serializer):
    start_number = serializers.IntegerField(default=1)
    ignore_numbers = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    stage=serializers.IntegerField(required=True)
    gender = serializers.IntegerField(required=True)