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
        group = data.get('group')
        competitor = data.get('competitor')

        # Check if the group and competitor have compatible genders
        if group.gender != competitor.gender:
            raise serializers.ValidationError("Group and competitor have incompatible genders.")

        # Check if the competitor's birth year is within the group's year range
        # group_start_year, group_end_year = map(int, group.group_name.split()[1].split('-'))
        # competitor_birth_year = competitor.year
        # if competitor_birth_year == group_start_year or competitor_birth_year == group_end_year:
        #     pass
        # else:
        #     raise serializers.ValidationError("Competitor's birth year is not within the group's year range.")


        # Your existing code for checking uniqueness
        group_id = data.get('group')
        competitor_id = data.get('competitor')

        if not self.instance:
            if Cart.objects.filter(group=group_id, competitor=competitor_id).exists():
                raise serializers.ValidationError("A result for this group and competitor already exists.")
        else:
            if Cart.objects.exclude(pk=self.instance.pk).filter(group=group_id, competitor=competitor_id).exists():
                raise serializers.ValidationError("A result for this group and competitor already exists with a different ID.")

        return data


class ResultsSerializer(serializers.ModelSerializer):
    cart_detail = CartSerializer(source='competitor', read_only=True)

    POINTS_TABLE = {
        1: 25, 2: 20, 3: 15, 4: 10, 5: 8,
        6: 6, 7: 4, 8: 3, 9: 2, 10: 1
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

        competitor_id = instance.competitor.competitor.id
        season_id = instance.competitor.group.competition.stage.season.id

        # Calculate total run time only if both runs are provided
        if instance.run1 and instance.run2:
            if instance.run1 in ["DNF","DNS"] or instance.run2 in ["DNF","DNS"]:
                instance.run_total = None
            else:
                instance.run_total = self.sum_times(instance.run1, instance.run2)
                instance.point = self.POINTS_TABLE.get(instance.place, 0)

        elif instance.run1:
            if instance.run1 in ["DNF","DNS"]:
                instance.run_total = None
            else:
                instance.run_total = instance.run1

        elif instance.run2:
            if instance.run2 in ["DNF","DNS"]:
                instance.run_total = None
            else:
                instance.run_total = instance.run2
                instance.point = self.POINTS_TABLE.get(instance.place, 0)

        instance.save()

        self.recalculate_placements(instance)
        self.recalculate_season_points(competitor_id, season_id)
        self.recalculate_all_season_points(season_id)

        return instance


    def recalculate_placements(self, instance):
        all_results = Results.objects.filter(
            competitor__group=instance.competitor.group
        ).order_by('run_total')

        all_results_count = Results.objects.filter(
            competitor__group=instance.competitor.group
        ).order_by('run_total').count()

        normal_placement = 1
        for result in all_results:
            if result.run1 not in ["DNF","DNS"] and result.run2 not in ["DNF","DNS"]:
                result.place = normal_placement
                normal_placement += 1
                result.point = self.POINTS_TABLE.get(result.place, 0)
            else:
                result.place = all_results_count
                result.point = 0
                all_results_count -= 1

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


