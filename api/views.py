from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import StaticWeapon
from api.serializers import StaticWeaponSerializer

# Create your views here.
class StaticWeaponViewset(ModelViewSet):
  serializer_class = StaticWeaponSerializer
  queryset = StaticWeapon.objects.all()

def index_view(request):
  return render(request, 'index.html', {'weapon': StaticWeapon.objects.get(name="Crimil's Dagger")})