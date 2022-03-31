from django.contrib import admin
from api.models import StaticWeapon, PlugSet, WishlistWeapon

# Register your models here.
admin.site.register(StaticWeapon)
admin.site.register(PlugSet)
admin.site.register(WishlistWeapon)