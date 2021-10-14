from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import StaticWeapon, Plug, PlugSet
from api.serializers import StaticWeaponSerializer, PlugSerializer, PlugSetSerializer

# Create your views here.
class StaticWeaponViewset(ModelViewSet):
  serializer_class = StaticWeaponSerializer
  queryset = StaticWeapon.objects.all()
  
  def get_queryset(self):
    queryset = StaticWeapon.objects.all()
    hash = self.request.query_params.get('hash')
    if hash is not None:
      queryset = queryset.filter(hash=hash)
    return queryset

class PlugViewset(ModelViewSet):
  serializer_class = PlugSerializer
  queryset = Plug.objects.all()

class PlugSetViewset(ModelViewSet):
  serializer_class = PlugSetSerializer
  queryset = PlugSet.objects.all()

def index_view(request):
  weapon = StaticWeapon.objects.get(hash=1789347249)
  column_one = weapon.column_one_hash.reusable_plug_items.all()
  plugset = PlugSet.objects.get(hash=3541408343)
  reusable_items = plugset.reusable_plug_items.all()
  weapons = StaticWeapon.objects.all().order_by('-index')
  return render(request, 'index.html', {'weapons': weapons})