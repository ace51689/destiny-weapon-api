from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from .models import StaticWeapon, Plug, PlugSet, WishlistWeapon
from rest_framework.response import Response

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
      'current_watermark',
      'original_watermark',
      'original_nonsunset_watermark',
      'season_information',
      'index',
      'is_sunset',
      'source_hash',
      'source_string',
      'column_one_hash',
      'column_two_hash',
      'column_three_hash',
      'column_four_hash',
      'origin_trait_hash'
    ]


class WishlistWeaponSerializer(ModelSerializer):
  class Meta:
    model = WishlistWeapon
    fields = [
      'hash',
      'name',
      'vanguard',
      'crucible',
      'gambit',
      'junk'
    ]


class CreateWishlistWeaponSerializer(ModelSerializer):
  class Meta:
    model = WishlistWeapon
    fields = ('hash', 'vanguard', 'crucible', 'gambit',)
      

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