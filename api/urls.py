from django.urls import path
from django.conf.urls import include
from rest_framework import routers

from api.views import PlugSetViewset, StaticWeaponViewset, PlugViewset, WishlistWeaponViewset

router = routers.DefaultRouter()

router.register('static-weapon', StaticWeaponViewset)
router.register('plug', PlugViewset)
router.register('plug-sets', PlugSetViewset)
# router.register('wishlist-weapons', WishlistWeaponViewset)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/wishlist-weapons/', WishlistWeaponViewset.as_view(), name="wishlist-weapons")
]
