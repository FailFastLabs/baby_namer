from django.shortcuts import render, get_object_or_404
from .models import BabyName, NameRank

def baby_name_detail(request, baby_name):
    baby_name_data = get_object_or_404(BabyName, name=baby_name)
    baby_name_usage_data = get_object_or_404(NameRank, name=baby_name)
    famous_people = baby_name_data.famousperson_set.all()
    return render(request, 'app/baby_name_detail.html',
                  {'baby_name_data': baby_name_data,
                   'baby_name_usage_data': baby_name_usage_data,
                   'famous_people': famous_people})
