from django.contrib import admin
from .models import NameGender, Ethnicity, Religion, FamousPerson, BabyName, BabyNameRef, NameRank, NameStateRank

admin.site.register(NameGender)
admin.site.register(Ethnicity)
admin.site.register(Religion)
admin.site.register(FamousPerson)
admin.site.register(BabyName)
admin.site.register(BabyNameRef)
admin.site.register(NameRank)
admin.site.register(NameStateRank)