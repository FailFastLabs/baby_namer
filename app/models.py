from django.db import models
from django.core.validators import MinValueValidator, URLValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    gender = models.CharField(max_length=10, choices=NameGender.choices)
    description = models.TextField(null=True, blank=True)
    boy_rank = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(-2)])
    girl_rank = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(-2)])
    name_variants = models.JSONField(null=True, blank=True)
    ethnicity = models.JSONField(null=True, blank=True)
    religion = models.JSONField(null=True, blank=True)
    language = models.JSONField(null=True, blank=True)
    region = models.JSONField(null=True, blank=True)
    sort_order = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    """
    def clean(self):
        # Validate ethnicity
        if self.ethnicity is not None:
            tmp = self.ethnicity
            if tmp is str:
                tmp = [tmp]
            for ethnicity in tmp:
                if ethnicity not in [e.value for e in Ethnicity]:
                    raise ValidationError({
                        'ethnicity': ValidationError('Invalid ethnicity: %(ethnicity)s',
                                                     params={'ethnicity': ethnicity}),
                    })

        # Validate religion
        if self.religion is not None:
            tmp = self.religion
            if tmp is str:
                tmp = [tmp]
            for religion in self.religion:
                if religion not in [r.value for r in Religion]:
                    raise ValidationError({
                        'religion': ValidationError('Invalid religion: %(religion)s', params={'religion': religion}),
                    })
    """                    

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
    def get_tags(self):
        tags = BabyTags.objects.filter(baby_name=self)
        return tags
    def get_famous_people(self):
        return FamousPerson.objects.filter(baby_name=self)

class FamousPerson(models.Model):
    name = models.CharField(max_length=255)
    first_name = models.ForeignKey(
        BabyName,
        on_delete=models.CASCADE
    )
    description = models.TextField(null=True, blank=True)
    wikipedia_link = models.URLField(validators=[URLValidator()], primary_key=True)
    popularity_score = models.FloatField(null=True, blank=True)


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

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    baby_name = models.ForeignKey(BabyName, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'baby_name',)

class BabyTags(models.Model):
    baby_name = models.ForeignKey(BabyName, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    class Meta:
        unique_together = ('baby_name', 'key', 'value')