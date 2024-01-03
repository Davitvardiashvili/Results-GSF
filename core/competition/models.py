from django.db import models


class Gender(models.Model):
    gender = models.CharField(unique=True, max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gender
    

class Status(models.Model):
    status = models.CharField(max_length=10, default='Active')

    def __str__(self):
        return self.status
    
class Discipline(models.Model):
    discipline = models.CharField(max_length=150)

    def __str__(self):
        return self.discipline


class School(models.Model):
    school_name = models.CharField(unique=True, max_length=60)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.school_name

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


class Stage(models.Model):
    name = models.CharField(max_length=50)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.season} - {self.name}'

class CompetitionDay(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    period = models.DateField()
    
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.stage} - {self.discipline}'


class Group(models.Model):
    competition = models.ForeignKey(CompetitionDay, on_delete=models.CASCADE)
    group_name = models.CharField(max_length=100)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)

    def __str__(self):
        return self.group_name


class Cart(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE, null=True)
    bib_number = models.IntegerField(blank=True, null=True)


    
class Results(models.Model):
    place = models.IntegerField(null=True, blank=True)
    competitor = models.ForeignKey(Cart,  on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, null=True, on_delete=models.SET_NULL, default=1)
    run1 = models.CharField(max_length=50, null=True, blank=True) 
    run2 = models.CharField(max_length=50, null=True, blank=True)
    run_total = models.CharField(max_length=50, null=True, blank=True)
    point = models.IntegerField(null=True, blank=True)
    season_point = models.IntegerField(null=True, blank=True)
