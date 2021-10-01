from django.conf.urls import include, url
from .views import StaticWeaponViewset
from rest_framework import routers

router = routers.DefaultRouter()

router.register('static-weapon', StaticWeaponViewset)

urlpatterns = [
  url(r'api/', include(router.urls))
]