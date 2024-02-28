from django.contrib import admin
from api.models import StaticWeapon, PlugSet, WishlistWeapon, Plug

# Register your models here.
admin.site.register(Plug)
admin.site.register(PlugSet)
admin.site.register(StaticWeapon)
admin.site.register(WishlistWeapon)
