from rest_framework.viewsets import ModelViewSet
from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions, status
from rest_framework.response import Response

from recipe.models import (Ingredient, Recipe, Favorite,
                           ShoppingCart, RecipeIngredient)
from user.models import Subscription, User
from recipe.serializers import (IngredientSerializer, RecipeSerializer,
                                UserSerializer)
from recipe.permissions import IsAuthorOrReadOnly


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all().order_by('name')
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('-date_published')
        params = self.request.query_params

        author_id = params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        if self.request.user.is_authenticated:
            is_in_shopping_cart = params.get('is_in_shopping_cart')
            if is_in_shopping_cart is not None:
                if is_in_shopping_cart == '1':
                    queryset = queryset.filter(
                        shoppingcart__user=self.request.user
                    )
                elif is_in_shopping_cart == '0':
                    queryset = queryset.exclude(
                        shoppingcart__user=self.request.user
                    )

            is_favorited = params.get('is_favorited')
            if is_favorited is not None:
                if is_favorited == '1':
                    queryset = queryset.filter(
                        favorite__user=self.request.user
                    )
                elif is_favorited == '0':
                    queryset = queryset.exclude(
                        favorite__user=self.request.user
                    )

        return queryset.distinct()

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    @staticmethod
    def handle_fav_or_cart(request, model, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == "POST":
            _, created = model.objects.get_or_create(user=user, recipe=recipe)
            if created:
                return Response(
                    {'status': 'Рецепт добавлен'},
                    status=status.HTTP_201_CREATED)
            return Response(
                {'status': 'Рецепт уже есть в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
