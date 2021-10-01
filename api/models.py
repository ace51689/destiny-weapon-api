from django.db import models

# Create your models here.
class StaticWeapon(models.Model):
  hash = models.PositiveBigIntegerField(primary_key=True)
  weapon_dict = models.JSONField()