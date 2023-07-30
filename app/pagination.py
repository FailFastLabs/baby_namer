from .models import BabyName, Favorite, BabyTags
from django.core.paginator import Paginator
# from itertools import chain

def paginate_favorites(page_number, user, n):
    names = Favorite.objects.filter(user=user).order_by('baby_name')
    names = [name.baby_name for name in names]
    names = __f(names)
    paginator = Paginator(names, n)
    print(names)
    return paginator.get_page(page_number)

def __f(names):
    return [[name] for name in names]
def paginate_names(page_number, gender, n):
    if gender == 'boys':
        names = BabyName.objects.order_by('boy_rank').exclude(boy_rank__isnull=True)[0:1000] # TODO get rid of -1 rank
        tags = BabyTags.objects.filter(baby_name__in=names)

        for name in names:
            name.rank = name.boy_rank
            name.tags=tags.filter(baby_name=name)
        names = __f(names)
    elif gender == 'girls':
        names = BabyName.objects.order_by('girl_rank').exclude(girl_rank__isnull=True)[0:1000]
        tags = BabyTags.objects.filter(baby_name__in=names)

        for name in names:
            name.rank = name.girl_rank
            name.tags=tags.filter(baby_name=name)
        names = __f(names)
    else:
        boy_names = BabyName.objects.order_by('boy_rank').exclude(boy_rank__isnull=True)[0:1000]
        girl_names = BabyName.objects.order_by('girl_rank').exclude(girl_rank__isnull=True)[0:1000]
        tags_1 = BabyTags.objects.filter(baby_name__in=boy_names)
        tags_2 = BabyTags.objects.filter(baby_name__in=girl_names) # TODO MAKE THIS FASTER

        for name in boy_names:
            name.rank = name.boy_rank
            name.tags = tags_1.filter(baby_name=name)
        for name in girl_names:
            name.rank = name.girl_rank
            name.tags = tags_2.filter(baby_name=name)
            print(name.girl_rank)
        names = list(zip(boy_names, girl_names))
    paginator = Paginator(names, n)
    return paginator.get_page(page_number)