from django.contrib import admin
from .models import FamousPerson, BabyName, NameRank, Embedding, Favorite, BabyTags

admin.site.register(FamousPerson)
admin.site.register(NameRank)
admin.site.register(Embedding)
admin.site.register(Favorite)
admin.site.register(BabyTags)

class FamousPersonInline(admin.TabularInline):
    model = FamousPerson

class BabyTagsInline(admin.TabularInline):
    model = BabyTags

class NameRankInline(admin.TabularInline):
    model = NameRank
    extra = 0
    ordering = ['year']  # Order the NameRank instances by year


class BabyNameAdmin(admin.ModelAdmin):
    inlines = [FamousPersonInline, BabyTagsInline]
    list_display = ['name', 'gender', 'description', 'boy_rank', 'girl_rank']
    ordering = ['sort_order']  # Order the BabyName objects by name
    search_fields = ['name', 'description']  # Add search fields for name and description

admin.site.register(BabyName, BabyNameAdmin)