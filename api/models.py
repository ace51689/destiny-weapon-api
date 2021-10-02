from django.db import models
from django.db.models import manager

# Create your models here.
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
  column_one_hash = models.PositiveBigIntegerField(null=True, editable=False)
  column_two_hash = models.PositiveBigIntegerField(null=True, editable=False)
  column_three_hash = models.PositiveBigIntegerField(null=True, editable=False)
  column_four_hash = models.PositiveBigIntegerField(null=True, editable=False)

  def __str__(self):
    return self.name