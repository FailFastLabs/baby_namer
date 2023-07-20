from django.db import models
from django.core.validators import MinValueValidator, URLValidator

class NameGender(models.TextChoices):
    MALE = 'Male'
    FEMALE = 'Female'
    UNISEX = 'Unisex'


class Ethnicity(models.TextChoices):
    AFRICAN = 'African'
    ASIAN = 'Asian'
    CAUCASIAN = 'Caucasian'
    HISPANIC = 'Hispanic'
    MIDDLE_EASTERN = 'Middle Eastern'
    NATIVE_AMERICAN = 'Native American'
    PACIFIC_ISLANDER = 'Pacific Islander'
    TWO_OR_MORE_RACES = 'Two or More Races'
    OTHER = 'Other'
    UNKNOWN = 'Unknown'

    def __str__(self):
        return self.value

class Religion(models.TextChoices):
    CHRISTIANITY = 'Christianity'
    ISLAM = 'Islam'
    SECULAR = 'Secular'
    HINDUISM = 'Hinduism'
    BUDDHISM = 'Buddhism'
    JUDAISM = 'Judaism'
    SIKHISM = 'Sikhism'
    BAHAI = 'Bahai'
    JAINISM = 'Jainism'
    SHINTO = 'Shinto'

class BabyName(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    gender = models.CharField(max_length=10,choices = NameGender.choices)
    description = models.TextField(null=True, blank=True)
    boy_rank = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(-2)])
    girl_rank = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(-2)])
    name_variants = models.JSONField(null=True, blank=True)
    ethnicity = models.CharField(max_length=50, choices=Ethnicity.choices, null=True, blank=True)
    religion = models.CharField(max_length=50, choices=Religion.choices, null=True, blank=True)
    language = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    sort_order = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])

    def __getattr__(self, name):
        if name in ['gender', 'ethnicity', 'religion']:
            value = self.__dict__[name]
            if value is not None:
                if name == 'gender':
                    return NameGender(value)
                elif name == 'ethnicity':
                    return Ethnicity(value)
                elif name == 'religion':
                    return Religion(value)
        return super().__getattr__(name)
class FamousPerson(models.Model):
    name = models.CharField(max_length=255)
    first_name = models.ForeignKey(
        BabyName,
        on_delete=models.CASCADE
    )
    description = models.TextField(null=True, blank=True)
    wikipedia_link = models.URLField(validators=[URLValidator()], primary_key=True)


class NameRank(models.Model):
    name = models.ForeignKey(
        BabyName,
        on_delete=models.CASCADE
    )
    gender = models.CharField(max_length=10, choices=NameGender.choices)
    year = models.IntegerField(validators=[MinValueValidator(0)])
    count = models.IntegerField(validators=[MinValueValidator(0)])
    rank = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('name', 'gender', 'year')


class NameStatePopularity(models.Model):
    name = models.ForeignKey(
        BabyName,
        on_delete=models.CASCADE
    )
    state = models.CharField(max_length=15)
    relative_popularity = models.FloatField()

    class Meta:
        unique_together = ('name', 'state')


class Embedding(models.Model):
    name = models.ForeignKey(
        BabyName,
        on_delete=models.CASCADE
    )
    embedding = models.JSONField(null=True, blank=True)