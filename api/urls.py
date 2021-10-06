from django.conf.urls import include, url
from .views import PlugSetViewset, StaticWeaponViewset, PlugViewset
from rest_framework import routers

router = routers.DefaultRouter()

router.register('static-weapon', StaticWeaponViewset)
router.register('plug', PlugViewset)
router.register('plug-sets', PlugSetViewset)

urlpatterns = [
  url(r'api/', include(router.urls))
]