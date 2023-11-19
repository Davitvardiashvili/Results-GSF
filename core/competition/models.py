from django.db import models


class School(models.Model):
    school_name = models.CharField(unique=True, max_length=60)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.school_name


class Gender(models.Model):
    gender = models.CharField(unique=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gender


class Competitor(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True)
    year = models.IntegerField()
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} {self.surname}'


class Season(models.Model):
    season = models.CharField(max_length=50)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.season


class Discipline(models.Model):
    discipline = models.CharField(unique=True, max_length=150)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.season} - {self.discipline}'


class Stage(models.Model):
    name = models.CharField(max_length=50)
    discipline = models.ForeignKey(Discipline, on_delete=models.SET_NULL, null=True)
    period = models.DateField()

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.discipline} - {self.name} - {self.period}'


class Group(models.Model):
    grop_name = models.CharField(max_length=100)
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.grop_name


class Cart(models.Model):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    competitor = models.ForeignKey(Competitor, on_delete=models.SET_NULL, null=True)
    bib_number = models.IntegerField(blank=True, null=True)


class Results(models.Model):
    place = models.IntegerField(null=True, blank=True)
    competitor = models.ForeignKey(Competitor, on_delete=models.SET_NULL, null=True)
    competition = models.ForeignKey(Cart,  on_delete=models.SET_NULL, null=True)
    run1 = models.CharField(max_length=50, null=True, blank=True)
    run2 = models.CharField(max_length=50, null=True, blank=True)
    run_total = models.CharField(max_length=50, null=True, blank=True)
    point = models.IntegerField(null=True, blank=True)
    season_point = models.IntegerField(null=True, blank=True)
