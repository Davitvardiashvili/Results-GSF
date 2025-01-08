from django.db import models


# -- Simple reference models --

class Gender(models.Model):
    """
    E.g., Male, Female, etc.
    """
    name = models.CharField(unique=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Discipline(models.Model):
    """
    E.g., Slalom, Giant Slalom, etc.
    """
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class School(models.Model):
    """
    School or club the competitor is associated with.
    """
    name = models.CharField(unique=True, max_length=60)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']


# -- Core competition data models --

class Season(models.Model):
    """
    A full season (e.g., 2024-2025).
    """
    season = models.CharField(max_length=50, unique=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.season

    class Meta:
        ordering = ['-id']


class AgeGroup(models.Model):
    """
    Example:
      - birth_year_start = 2008, birth_year_end = 2009  => 2008–2009
      - birth_year_start = 2005, birth_year_end = None => 2005 and older
    """
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name='age_groups'
    )
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    birth_year_start = models.IntegerField(null=True, blank=True)
    birth_year_end = models.IntegerField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Show different text depending on whether end is open
        if self.birth_year_end is None:
            return f"({self.gender}) {self.birth_year_start} and older"
        else:
            return f"({self.gender}) {self.birth_year_start} - {self.birth_year_end}"

    class Meta:
        ordering = ['-id']


class Stage(models.Model):
    """
    A stage in the season, e.g. 'Regional Cup Stage 1'.
    """
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='stages')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, null=True, blank=True)  # optional
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.season.season} - {self.name} - {self.location}"

    class Meta:
        ordering = ['-id']


class CompetitionDay(models.Model):
    """
    Each Stage can have multiple competition days with different disciplines.
    E.g., Day 1 (Slalom), Day 2 (Giant Slalom).
    """
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='competition_days')
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    date = models.DateField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stage} | {self.discipline} on {self.date}"

    class Meta:
        ordering = ['-id']


# -- People / Registration --

class Competitor(models.Model):
    """
    A competitor (athlete).
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True)
    year_of_birth = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['-id']


class Registration(models.Model):
    """
    Who is participating in a given day’s competition, in which group, with what bib number, etc.
    This replaces the 'Cart' model.
    """
    competition_day = models.ForeignKey(
        CompetitionDay,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    competitor = models.ForeignKey(
        Competitor,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    # If you also want to store an explicit AgeGroup link:
    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Age group competitor is competing in for this day."
    )
    bib_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.bib_number or '-'} - {self.competitor} ({self.competition_day})"


# -- Results --

class Result(models.Model):
    """
    Stores result data for a single competitor in a specific CompetitionDay.
    """
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='result'
    )

    # Times or run info
    run1_time = models.CharField(max_length=50, null=True, blank=True)
    run2_time = models.CharField(max_length=50, null=True, blank=True)
    total_time = models.CharField(max_length=50, null=True, blank=True)

    # Placement & points
    place = models.IntegerField(null=True, blank=True)
    points = models.IntegerField(null=True, blank=True)  # Points for this day
    season_points = models.IntegerField(null=True, blank=True)  # If you store aggregated season points here

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.registration} (Place: {self.place})"
