from rest_framework import routers

from apiv1 import viewsets

router = routers.SimpleRouter()
router.register('photos', viewsets.PhotoViewSet)

urlpatterns = router.urls