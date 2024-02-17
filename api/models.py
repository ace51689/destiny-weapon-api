from django.db import models

# Create your models here.
class Plug(models.Model):
  hash = models.PositiveBigIntegerField(primary_key=True, editable=False)
  name = models.CharField(max_length=100, editable=False)
  icon = models.CharField(max_length=100)
  description = models.TextField(editable=False)

  def __str__(self):
    return self.name

class PlugSet(models.Model):
  hash = models.PositiveBigIntegerField(primary_key=True, editable=False)
  reusable_plug_items = models.ManyToManyField('Plug', symmetrical=False, editable=False)

class StaticWeapon(models.Model):
  hash = models.PositiveBigIntegerField(primary_key=True, editable=False)
  name = models.CharField(max_length=100, editable=False)
  icon = models.CharField(max_length=100, editable=False)
  flavor_text = models.TextField(editable=False)
  tier_type = models.CharField(max_length=10, editable=False)
  weapon_type = models.CharField(max_length=30, editable=False)
  slot_type = models.CharField(max_length=7, editable=False)
  ammo_type = models.CharField(max_length=7, editable=False)
  damage_type = models.CharField(max_length=7, editable=False)
  watermark_icons = models.JSONField()
  current_watermark = models.CharField(max_length=100, editable=False, null=True)
  original_watermark = models.CharField(max_length=100, editable=False, null=True)
  original_nonsunset_watermark = models.CharField(max_length=100, editable=False, null=True)
  season_information = models.JSONField()
  index = models.PositiveBigIntegerField(editable=False)
  is_sunset = models.BooleanField(default=False)
  source_hash = models.PositiveBigIntegerField(editable=False)
  source_string = models.CharField(max_length=120, editable=False)
  column_one_hash = models.ForeignKey('PlugSet', related_name='column_one', on_delete=models.SET_NULL, null=True, blank=True)
  column_two_hash = models.ForeignKey('PlugSet', related_name='column_two', on_delete=models.SET_NULL, null=True, blank=True)
  column_three_hash = models.ForeignKey('PlugSet', related_name='column_three', on_delete=models.SET_NULL, null=True, blank=True)
  column_four_hash = models.ForeignKey('PlugSet', related_name='column_four', on_delete=models.SET_NULL, null=True, blank=True)
  origin_trait_hash = models.ForeignKey('PlugSet', related_name='origin_trait', on_delete=models.SET_NULL, null=True, blank=True)

  def __str__(self):
    return self.name

class WishlistWeapon(models.Model):
  hash = models.PositiveBigIntegerField(primary_key=True)
  name = models.CharField(max_length=100, editable=False)
  vanguard = models.JSONField(null=True, blank=True)
  crucible = models.JSONField(null=True, blank=True)
  gambit = models.JSONField(null=True, blank=True)
  junk = models.JSONField(null=True, blank=True)

  def __str__(self):
      return self.name
