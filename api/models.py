from django.db import models

# Create your models here.
class StaticWeapon(models.Model):
  hash = models.PositiveBigIntegerField(primary_key=True, editable=False)
  name = models.CharField(max_length=100)
  weapon_dict = models.JSONField(editable=False)

  def __str__(self):
    return self.name