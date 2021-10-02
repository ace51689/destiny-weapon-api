from rest_framework.serializers import ModelSerializer
from .models import StaticWeapon

class StaticWeaponSerializer(ModelSerializer):
  class Meta:
    model = StaticWeapon
    fields = [
      'hash',
      'name',
      'icon',
      'flavor_text',
      'tier_type',
      'weapon_type',
      'slot_type',
      'ammo_type',
      'damage_type',
      'watermark_icons',
      'column_one_hash',
      'column_two_hash',
      'column_three_hash',
      'column_four_hash',
    ]