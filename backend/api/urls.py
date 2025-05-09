from rest_framework.routers import SimpleRouter
from django.urls import include, path

router = SimpleRouter()
# TODO когда вьюшки сделаешь тут их пропиши пж

urlpatterns = [
    path('', include(router.urls)),
    path('auth', include('djoser.urls.authtoken'))
]
