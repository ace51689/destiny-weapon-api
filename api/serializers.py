from rest_framework.serializers import ModelSerializer
from .models import StaticWeapon

class StaticWeaponSerializer(ModelSerializer):
  class Meta:
    model = StaticWeapon
    fields = [
      'hash',
      'name',
      'weapon_dict'
    ]