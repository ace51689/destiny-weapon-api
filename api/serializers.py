from rest_framework.serializers import ModelSerializer
from .models import StaticWeapon, Plug, PlugSet

class StaticWeaponSerializer(ModelSerializer):
  class Meta:
    model = StaticWeapon
    depth = 2
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
      'index',
      'is_sunset',
      'column_one_hash',
      'column_two_hash',
      'column_three_hash',
      'column_four_hash',
    ]

class PlugSerializer(ModelSerializer):
  class Meta:
    model = Plug
    fields = [
      'hash',
      'name',
      'icon',
      'description'
    ]

class PlugSetSerializer(ModelSerializer):
  class Meta:
    model = PlugSet
    fields = [
      'hash',
      'reusable_plug_items'
    ]