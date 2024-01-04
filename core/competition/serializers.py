from rest_framework import serializers
from .models import *
from datetime import datetime, timedelta
from rest_framework.authtoken.models import Token
from django.db.models import Sum
class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key',)

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
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


class StageSerializer(serializers.ModelSerializer):
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True,
    )
    season = SeasonSerializer(read_only=True)
    class Meta:
        model = Stage
        fields = ['id', 'season','season_id' ,'name']


class CompetitionDaySerializer(serializers.ModelSerializer):
    stage_id = serializers.PrimaryKeyRelatedField(
        queryset=Stage.objects.all(),
        source='stage',
        write_only=True,
    )
    discipline_id = serializers.PrimaryKeyRelatedField(
        queryset=Discipline.objects.all(),
        source='discipline',
        write_only=True,
    )
    stage = StageSerializer(read_only=True) 
    discipline = DisciplineSerializer(read_only=True) 

    class Meta:
        model = CompetitionDay
        fields = ['id', 'discipline','discipline_id','period', 'stage_id', 'stage']

class GroupSerializer(serializers.ModelSerializer):
    gender_id = serializers.PrimaryKeyRelatedField(
        queryset=Gender.objects.all(), 
        source='gender', 
        write_only=True
    )

    competition_id = serializers.PrimaryKeyRelatedField(
        queryset=CompetitionDay.objects.all(), 
        source='competition', 
        write_only=True
    )

    competition = CompetitionDaySerializer(read_only=True)
    gender = serializers.CharField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'competition', 'competition_id', 'gender', 'gender_id']


class CartSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    competitor_id = serializers.PrimaryKeyRelatedField(
        queryset=Competitor.objects.all(), 
        source='competitor', 
        write_only=True
    )

    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), 
        source='group', 
        write_only=True
    )
    group = GroupSerializer(read_only=True)
    competitor = CompetitorSerializer(read_only=True)
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
            if Cart.objects.filter(group=group_id, competitor=competitor_id).exists():
                raise serializers.ValidationError("A result for this group and competitor already exists.")
        else:
            # This is an update, check if the combination exists elsewhere
            if Cart.objects.exclude(pk=self.instance.pk).filter(group=group_id, competitor=competitor_id).exists():
                raise serializers.ValidationError("A result for this group and competitor already exists with a different ID.")

        return data


class ResultsSerializer(serializers.ModelSerializer):
    cart_detail = CartSerializer(source='competitor', read_only=True)
    status = serializers.CharField(source='status.status', read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), 
        source='status', 
        write_only=False  # Allow both read and write operations
    )
    DNF_ID = 2
    DNS_ID = 3
    POINTS_TABLE = {
        1: 25, 2: 20, 3: 15, 4: 12, 5: 11,
        6: 10, 7: 9, 8: 8, 9: 7, 10: 6,
        11: 5, 12: 4, 13: 3, 14: 2, 15: 1
    }


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
        # Update run times only if they are provided in the payload
        if 'run1' in validated_data:
            instance.run1 = validated_data.get('run1')
        if 'run2' in validated_data:
            instance.run2 = validated_data.get('run2')

        # Calculate total run time only if both runs are provided
        if instance.run1 and instance.run2:
            instance.run_total = self.sum_times(instance.run1, instance.run2)
            self.recalculate_placements(instance)  # Call this only when both runs are available
        elif instance.run1:
            instance.run_total = instance.run1
            self.recalculate_placements(instance)
        elif instance.run2:
            instance.run_total = instance.run2
            self.recalculate_placements(instance)

        # Update status and set points accordingly
        status = validated_data.get('status', instance.status)
        instance.status = status
        if status and status.id in [self.DNF_ID, self.DNS_ID]:
            instance.point = 0
            instance.place = 999  # Temporary high value
        else:
            # Normal point calculation
            instance.point = self.POINTS_TABLE.get(instance.place, 0)

        # Save the instance with updated data
        instance.save()

        # Recalculate placements and season points for the group if status changes
        if 'status' in validated_data:
            self.recalculate_placements(instance)
            competitor_id = instance.competitor.competitor.id
            season_id = instance.competitor.group.competition.stage.season.id
            self.recalculate_season_points(competitor_id, season_id)
            self.recalculate_all_season_points(season_id)

        return instance


    def recalculate_placements(self, instance):
        all_results = Results.objects.filter(
            competitor__group=instance.competitor.group
        ).order_by('run_total')

        normal_placement = 1
        for result in all_results:
            if result.status.id not in [self.DNF_ID, self.DNS_ID]:
                result.place = normal_placement
                normal_placement += 1
                result.point = self.POINTS_TABLE.get(result.place, 0)
                result.save(update_fields=['place', 'point'])

        # Handle DNF and DNS after assigning placements to others
        for result in all_results:
            if result.status.id in [self.DNF_ID, self.DNS_ID]:
                result.place = normal_placement
                result.point = 0
                normal_placement += 1
                result.save(update_fields=['place', 'point'])

    def recalculate_season_points(self, competitor_id, season_id):
        # Sum all points earned by this competitor in this season
        season_points = Results.objects.filter(
            competitor__competitor__id=competitor_id, 
            competitor__group__competition__stage__season__id=season_id
        ).aggregate(Sum('point'))['point__sum'] or 0

        # Update the season points for this competitor in all their results this season
        Results.objects.filter(
            competitor__competitor__id=competitor_id,
            competitor__group__competition__stage__season__id=season_id
        ).update(season_point=season_points)


    def recalculate_all_season_points(self, season_id):
        # Fetch all competitors in the season
        competitors_in_season = Competitor.objects.filter(
            cart__group__competition__stage__season__id=season_id
        ).distinct()

        # Recalculate season points for each competitor
        for competitor in competitors_in_season:
            self.recalculate_season_points(competitor.id, season_id)
    class Meta:
        model = Results
        fields = '__all__'


class RandomizeBibNumbersSerializer(serializers.Serializer):
    start_number = serializers.IntegerField(default=1)
    ignore_numbers = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    competition=serializers.IntegerField(required=True)
    gender = serializers.IntegerField(required=True)


