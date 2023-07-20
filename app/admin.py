from django.contrib import admin
from .models import FamousPerson, BabyName, NameRank, Embedding

admin.site.register(FamousPerson)
admin.site.register(BabyName)
admin.site.register(NameRank)
admin.site.register(Embedding)

