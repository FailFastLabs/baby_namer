from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.models import BabyName, Favorite

from django.shortcuts import render, get_object_or_404
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def favorite_baby_name(request):
    baby_name_id = request.data.get('baby_name_id')
    if not baby_name_id:
        return Response({'error': 'Missing baby_name_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        baby_name = BabyName.objects.get(name=baby_name_id)
    except BabyName.DoesNotExist:
        return Response({'error': 'BabyName not found'}, status=status.HTTP_404_NOT_FOUND)

    favorite, created = Favorite.objects.get_or_create(user=request.user, baby_name=baby_name)

    if not created:
        print('delete')
        # if favorite already exists, delete it
        favorite.delete()
        return Response({'status': 'unfavorited'})
    print('created')
    return Response({'status': 'favorited'})
