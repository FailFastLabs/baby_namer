from .models import BabyName, Favorite
from django.core.paginator import Paginator


def __f(names):
    return [[name] for name in names]

def paginate_favorites(page_number, user, n):
    names = Favorite.objects.filter(user=user).order_by('baby_name')
    names = [name.baby_name for name in names]
    names = __f(names)
    paginator = Paginator(names, n)
    print(names)
    return paginator.get_page(page_number)
def paginate_names(page_number, gender, n):


    if gender == 'boys':
        names = BabyName.objects.filter(boy_rank__gt=0).order_by('boy_rank') # TODO get rid of -1 rank
        for name in names:
            name.rank = name.boy_rank # TODO make unified min_rank for this
        names = __f(names)

    elif gender == 'girls':
        names = BabyName.objects.filter(girl_rank__gt=0).order_by('girl_rank')
        for name in names:
            name.rank = name.girl_rank
        names = __f(names)
    else:
        boy_names = BabyName.objects.filter(boy_rank__gt=0).order_by('boy_rank')
        girl_names = BabyName.objects.filter(girl_rank__gt=0).order_by('girl_rank')
        for name in boy_names:
            name.rank = name.boy_rank
        for name in girl_names:
            name.rank = name.girl_rank
        names = list(zip(boy_names, girl_names))
    paginator = Paginator(names, n)
    return paginator.get_page(page_number)