from rest_framework import serializers
from datetime import timedelta
from django.db.models import Sum
from rest_framework.authtoken.models import Token
from .models import (
    Gender,
    Discipline,
    School,
    Season,
    AgeGroup,
    Stage,
    CompetitionDay,
    Competitor,
    Registration,
    Result,
)


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
    """
    Example:
        POST/PUT with:
          {
            "first_name": "John",
            "last_name": "Doe",
            "gender_id": 1,
            "school_id": 2,
            "year_of_birth": 2008
          }
    """
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

    # Read-only display of related info
    gender = serializers.CharField(source='gender.name', read_only=True)
    school = serializers.CharField(source='school.name', read_only=True)

    class Meta:
        model = Competitor
        fields = [
            'id', 'first_name', 'last_name',
            'year_of_birth', 'gender_id', 'school_id',
            'gender', 'school'
        ]


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['id', 'season', 'created', 'updated']


class AgeGroupSerializer(serializers.ModelSerializer):
    """
    Example AgeGroup model fields:
      - season (FK)
      - group_name
      - gender
      - birth_year_start
      - birth_year_end
    """
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True
    )
    gender_id = serializers.PrimaryKeyRelatedField(
        queryset=Gender.objects.all(),
        source='gender',
        write_only=True
    )

    season = SeasonSerializer(read_only=True)
    gender = serializers.CharField(source='gender.name', read_only=True)

    class Meta:
        model = AgeGroup
        fields = [
            'id', 'season_id', 'gender_id',
            'season', 'gender',
            'birth_year_start', 'birth_year_end'
        ]


class StageSerializer(serializers.ModelSerializer):
    season_id = serializers.PrimaryKeyRelatedField(
        queryset=Season.objects.all(),
        source='season',
        write_only=True,
    )
    season = SeasonSerializer(read_only=True)

    class Meta:
        model = Stage
        fields = [
            'id', 'season_id', 'season',
            'name', 'location',
            'created', 'updated'
        ]


class CompetitionDaySerializer(serializers.ModelSerializer):
    stage_id = serializers.PrimaryKeyRelatedField(
        queryset=Stage.objects.all(),
        source='stage',
        write_only=True
    )
    discipline_id = serializers.PrimaryKeyRelatedField(
        queryset=Discipline.objects.all(),
        source='discipline',
        write_only=True
    )

    stage = StageSerializer(read_only=True)
    discipline = DisciplineSerializer(read_only=True)

    class Meta:
        model = CompetitionDay
        fields = [
            'id', 'stage_id', 'stage',
            'discipline_id', 'discipline',
            'date', 'created', 'updated'
        ]


class RegistrationSerializer(serializers.ModelSerializer):
    competition_day_id = serializers.PrimaryKeyRelatedField(
        queryset=CompetitionDay.objects.all(),
        source='competition_day',
        write_only=True
    )
    competitor_id = serializers.PrimaryKeyRelatedField(
        queryset=Competitor.objects.all(),
        source='competitor',
        write_only=True
    )
    age_group_id = serializers.PrimaryKeyRelatedField(
        queryset=AgeGroup.objects.all(),
        source='age_group',
        write_only=True,
        required=False,
        allow_null=True
    )

    # Read-only fields
    competition_day = CompetitionDaySerializer(read_only=True)
    competitor = CompetitorSerializer(read_only=True)
    age_group = AgeGroupSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id',
            'competition_day', 'competition_day_id',
            'competitor', 'competitor_id',
            'age_group', 'age_group_id',
            'bib_number'
        ]

    def validate(self, data):
        """
        Example: ensure competitor's gender matches age_group's gender if age_group is provided.
        """
        age_group = data.get('age_group')
        competitor = data.get('competitor')

        if age_group and competitor:
            if age_group.gender != competitor.gender:
                raise serializers.ValidationError("AgeGroup and competitor have incompatible genders.")

            # If you want to check birth year range
            if (age_group.birth_year_start and competitor.year_of_birth < age_group.birth_year_start) or \
                    (age_group.birth_year_end and competitor.year_of_birth > age_group.birth_year_end):
                raise serializers.ValidationError(
                    "Competitor's birth year is not within the AgeGroup's range."
                )

        # Ensure uniqueness: a competitor cannot be registered twice for the same day
        competition_day = data.get('competition_day')
        if not self.instance:
            if Registration.objects.filter(
                    competition_day=competition_day,
                    competitor=competitor
            ).exists():
                raise serializers.ValidationError("This competitor is already registered for that day.")
        else:
            if Registration.objects.exclude(pk=self.instance.pk).filter(
                    competition_day=competition_day,
                    competitor=competitor
            ).exists():
                raise serializers.ValidationError(
                    "This competitor is already registered for that day (on a different registration)."
                )

        return data


class ResultSerializer(serializers.ModelSerializer):
    """
    Replaces old `ResultsSerializer`.
    Uses `registration` (one-to-one) to link competitor & competition_day.
    """

    POINTS_TABLE = {
        1: 25, 2: 20, 3: 15, 4: 10, 5: 8,
        6: 6, 7: 4, 8: 3, 9: 2, 10: 1
    }

    registration_id = serializers.PrimaryKeyRelatedField(
        queryset=Registration.objects.all(),
        source='registration',
        required=False,  # <-- Add this
        write_only=True
    )
    registration = RegistrationSerializer(read_only=True)

    class Meta:
        model = Result
        fields = [
            'id',
            'registration_id', 'registration',
            'run1_time', 'run2_time', 'total_time',
            'place', 'points', 'season_points',
            'created', 'updated'
        ]

    def validate(self, data):
        """
        Check uniqueness of the result per registration.
        """
        registration_obj = data.get('registration')
        if not self.instance:
            if not registration_obj:
                raise serializers.ValidationError("registration_id is required on creation.")
            # Creating new
            if Result.objects.filter(registration=registration_obj).exists():
                raise serializers.ValidationError(
                    "A result for this registration already exists."
                )
        else:
            # Updating existing
            if Result.objects.exclude(pk=self.instance.pk).filter(registration=registration_obj).exists():
                raise serializers.ValidationError(
                    "A result for this registration already exists with a different ID."
                )
        return data

    def to_representation(self, instance):
        """
        Add extra fields to the output if needed.
        """
        response = super().to_representation(instance)
        # For convenience, rename them or add them
        response['run1_time'] = instance.run1_time
        response['run2_time'] = instance.run2_time
        response['total_time'] = instance.total_time
        response['points'] = instance.points
        response['season_points'] = instance.season_points
        return response

    # ----------------------------
    #     Time-Related Helpers
    # ----------------------------
    def validate_time(self, time_str):
        """
        Convert 'mm:ss,cc' to a timedelta for easier summing.
        Example: '01:23,45' => 1min 23s 450ms
        """
        if time_str in ["DNF", "DNS"]:
            # Return None if "DNF" or "DNS"
            return None

        try:
            minutes, seconds_centis = time_str.split(':')
            seconds, centiseconds = seconds_centis.split(',')
            time_delta = timedelta(
                minutes=int(minutes),
                seconds=int(seconds),
                milliseconds=int(centiseconds) * 10
            )
            return time_delta
        except Exception:
            raise serializers.ValidationError("Invalid time format. Use mm:ss,cc or DNF/DNS.")

    def sum_times(self, run1_str, run2_str):
        """
        Validate and sum two run times. Return the string in "mm:ss,cc" format.
        """
        run1_delta = self.validate_time(run1_str)
        run2_delta = self.validate_time(run2_str)

        if not run1_delta or not run2_delta:
            # If either is None => "DNF" or "DNS"
            return None

        run_total_delta = run1_delta + run2_delta

        total_minutes = run_total_delta.seconds // 60
        total_seconds = run_total_delta.seconds % 60
        # Convert microseconds to centiseconds
        total_centiseconds = run_total_delta.microseconds // 10000
        return f"{str(total_minutes).zfill(2)}:{str(total_seconds).zfill(2)},{str(total_centiseconds).zfill(2)}"

    # ----------------------------
    #         Update Logic
    # ----------------------------
    def update(self, instance, validated_data):
        """
        Update run times (run1_time, run2_time) and recalc total_time, place, points, etc.
        """
        run1_input = validated_data.get('run1_time', instance.run1_time)
        run2_input = validated_data.get('run2_time', instance.run2_time)

        instance.run1_time = run1_input
        instance.run2_time = run2_input

        # Calculate total time if both runs are valid
        if run1_input and run2_input:
            if run1_input in ["DNF", "DNS"] or run2_input in ["DNF", "DNS"]:
                instance.total_time = None
            else:
                instance.total_time = self.sum_times(run1_input, run2_input)
        else:
            # If only one run is present, keep that as total (unless DNF/DNS)
            single_run = run1_input or run2_input
            if single_run in ["DNF", "DNS"]:
                instance.total_time = None
            else:
                instance.total_time = single_run

        instance.save()

        # Recompute place & points within the relevant group
        self.recalculate_placements(instance)
        return instance

    # ----------------------------
    #       Recalculation
    # ----------------------------
    def recalculate_placements(self, instance):
        """
        Re-rank results for all competitors who share the same day + age group.
        Then reassign place & points. Finally, re-calc season points for everyone in that group.
        """
        reg = instance.registration
        age_group = reg.age_group
        competition_day = reg.competition_day

        queryset = Result.objects.filter(
            registration__competition_day=competition_day,
            registration__age_group=age_group
        )

        # Separate "completed" from DNF/DNS
        completed = [r for r in queryset if r.total_time is not None]
        dnfs = [r for r in queryset if r.total_time is None]

        def convert_time_str(t):
            # Convert "mm:ss,cc" -> integer for sorting
            mm, rest = t.split(':')
            ss, cc = rest.split(',')
            return int(mm) * 6000 + int(ss) * 100 + int(cc)

        completed.sort(key=lambda x: convert_time_str(x.total_time))

        place_counter = 1
        for r in completed:
            r.place = place_counter
            r.points = self.POINTS_TABLE.get(place_counter, 0)
            r.save(update_fields=['place', 'points'])
            place_counter += 1

        # DNF => after finishers
        for idx, r in enumerate(dnfs, start=place_counter):
            r.place = idx
            r.points = 0
            r.save(update_fields=['place', 'points'])

        # Now re-calc season points for **all** results in that group
        # Because changing a competitor's time might shift others' places & points
        self.recalc_all_season_points(queryset)

    def recalc_all_season_points(self, results_queryset):
        """
        For each competitor in results_queryset, recalc their season sum.
        """
        # Distill unique competitor IDs
        competitor_ids = list(
            results_queryset.values_list('registration__competitor_id', flat=True)
        )
        competitor_ids = set(competitor_ids)

        for comp_id in competitor_ids:
            # Recalculate the sum of points for *this* competitor across the season
            competitor_results = Result.objects.filter(
                registration__competitor_id=comp_id,
                registration__competition_day__stage__season=(
                    results_queryset.first().registration.competition_day.stage.season
                )
            )
            total_points = competitor_results.aggregate(Sum('points'))['points__sum'] or 0

            # Update them all with that new sum
            competitor_results.update(season_points=total_points)


class RandomizeBibNumbersSerializer(serializers.Serializer):
    start_number = serializers.IntegerField(default=1)
    ignore_numbers = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    competition_day_id = serializers.IntegerField(required=True)
    # Possibly also age_group_id or gender_id, depending on your logic
    age_group_id = serializers.IntegerField(required=False)
    # Or gender is not needed if age_group already includes gender

    # Then in your view or wherever you apply the randomization logic,
    # you'll fetch the relevant Registration objects and shuffle them.
