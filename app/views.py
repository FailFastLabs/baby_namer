from django.shortcuts import render, get_object_or_404
from .forms import BabyNameForm
#from .utils import process_baby_name_data, process_baby_name_usage_data, process_baby_name_state_data, process_year_rank_data, process_search_names, paginate_names, process_famous_people_data, paginate_favorites
from .data_processing import *
from .db_operations import *
from .pagination import paginate_names, paginate_favorites
from django.shortcuts import redirect
from .embeddings import get_related_names
from .models import BabyName, Favorite
MAX_NAMES = 20


def baby_name_detail(request, baby_name):
    baby_name_data = process_baby_name_data(baby_name)
    baby_name_usage_data = process_baby_name_usage_data(baby_name_data)
    states, relative_popularity = process_baby_name_state_data(baby_name_data)
    year_rank_data = process_year_rank_data(baby_name_usage_data, baby_name_data)
    famous_people = process_famous_people_data(baby_name_data)
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user, baby_name=baby_name).values_list('baby_name_id', flat=True)
    else:
        favorites = []
    return render(request, 'app/baby_name_details.html',
                  {'name': baby_name_data,
                   'baby_name_usage_data': year_rank_data,
                   'famous_people': famous_people,
                   'states': states,
                   'relative_popularity': relative_popularity,
                   'favorites': favorites
                   })

def popular_names_view(request, gender=None, n=20):
    page_number = request.GET.get('page', 1)
    names = paginate_names(page_number, gender, n)
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('baby_name_id', flat=True)
        # TODO improve query by only considering names wihtin request above
    else:
        favorites = []
    return render(request, 'app/index.html', {'page_obj': names, 'gender': gender, 'favorites': favorites})


def favorites_view(request, n=20):
    page_number = request.GET.get('page', 1)

    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user).values_list('baby_name_id', flat=True)
        names = paginate_favorites(page_number, request.user, n)
        # TODO improve query by only considering names wihtin request above
        messages = []
    else:
        favorites = []
        names = []
        messages = [{'message': 'You must be logged in to view your favorites.', 'tags': 'danger'}]

    # TODO improve query by only considering names wihtin request above
    return render(request, 'app/index.html', {'page_obj': names, 'gender': 'boys', 'favorites': favorites, 'messages': messages})


def search(request):
    q = request.GET.get('q', '').capitalize()
    form = BabyNameForm(request.GET)

    try:  # Exact match
        baby = BabyName.objects.get(name=q)
        return redirect('baby_name_detail', baby_name=baby.name)
    except BabyName.DoesNotExist:
        pass

    # Near string match
    if len(q.split(' ')) == 1 and len(q) < 15:  # no spaces, likely a direct name search
        names = BabyName.objects.filter(name__icontains=q)[:MAX_NAMES]
    else:
        names = None

    # Embedding match
    if not names:
        names = get_related_names(q, MAX_NAMES)  # Make sure this function is imported correctly
        names = [name[0] for name in names]

    return render(request, 'app/search.html', {'form': form, 'names': names})

def stats(request):
    from django.db.models import Count
    stats1=BabyName.objects.all().values('gender').annotate(total=Count('name')).order_by('total')
    stats2=BabyName.objects.filter(description__isnull=False).values('gender').annotate(total=Count('name')).order_by('total')
    print(stats1, stats2)
    return render(request, 'app/stats.html',{'data':[stats1, stats2]})