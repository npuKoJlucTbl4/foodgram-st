from rest_framework.routers import SimpleRouter
from django.urls import include, path

from .views import (UserViewSet, IngredientViewSet, RecipeViewSet)

router = SimpleRouter()
router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
