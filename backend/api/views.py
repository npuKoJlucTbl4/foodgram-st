from rest_framework.viewsets import ModelViewSet
from djoser.views import UserViewSet as DjoserUserViewSet
from django.urls import reverse
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework.exceptions import (ValidationError,
                                       NotAuthenticated)
from rest_framework.decorators import action
from rest_framework import permissions, status
from rest_framework.response import Response

from recipe.subfunctions import render_shopping_cart
from recipe.models import (Ingredient, Recipe, Favorite,
                           ShoppingCart, RecipeIngredient)
from user.models import Subscription, User
from recipe.serializers import (IngredientSerializer, RecipeSerializer,
                                UserSerializer, AvatarSerializer,
                                UserSubscriptionSerializer)
from recipe.permissions import IsAuthorOrReadOnly


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'head', 'options']
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all().order_by('name')
        name = self.request.query_params.get('name', '').strip()
        if name:
            queryset = queryset.filter(name__istartswith=name)
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
        if not self.request.user.is_authenticated:
            raise NotAuthenticated('Пользователь должен быть авторизирован')
        return serializer.save(author=self.request.user)

    @staticmethod
    def handle_fav_or_cart(request, model, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if not user.is_authenticated:
            return Response({'status':'Пользователь должен быть авторизирован'},
                            status=status.HTTP_401_UNAUTHORIZED)

        if request.method == "POST":
            _, created = model.objects.get_or_create(user=user, recipe=recipe)
            if created:
                return Response(
                    {
                        'id': recipe.id,
                        'name': recipe.name,
                        'image': request.build_absolute_uri(recipe.image.url)
                        if recipe.image else None,
                        'cooking_time': recipe.cooking_time},
                    status=status.HTTP_201_CREATED)
            return Response(
                {'status': 'Рецепт уже есть в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(model, user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        return self.handle_fav_or_cart(request, ShoppingCart, pk)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        return self.handle_fav_or_cart(request, Favorite, pk)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user

        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppingcart__user=user)
            .values('ingredient__name',
                    'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        recipes = Recipe.objects.filter(
            shoppingcart__user=user)

        shopping_cart_text = render_shopping_cart(user, ingredients, recipes)

        return FileResponse(
            shopping_cart_text,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_url = request.build_absolute_uri(
            reverse('short_link', args=[recipe.pk])
        ).split(':8000')
        short_url = short_url[0]+short_url[1]
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['me', 'avatar', 'subscriptions', 'subscribe']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['put', 'delete'], permission_classes=[
        permissions.IsAuthenticated], url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.method == 'DELETE':
            if not user.avatar:
                return Response(
                    {'error': 'Аватар отсутствует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                user.avatar.delete()
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)

        if 'avatar' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = AvatarSerializer(user, data=request.data, partial=True)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        serializer.save()
        return Response({"avatar": user.avatar.url}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[
        permissions.IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = request.user.subscribers.select_related(
            'author').prefetch_related('author__recipes')

        authors = [subscription.author for subscription in subscriptions]
        page = self.paginate_queryset(authors)
        serializer = UserSubscriptionSerializer(page, many=True, context={
            'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            raise ValidationError({'errors': 'Нельзя подписаться на себя'})

        if request.method == 'POST':
            _, created = Subscription.objects.get_or_create(
                user=user,
                author=author,
            )

            if not created:
                raise ValidationError({'errors': 'Вы уже подписаны'})

            serializer = UserSubscriptionSerializer(
                author,
                context={'request': request}
            )

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        
        if request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(user=user, author=author)
                subscription.delete()
                return Response(
                    {'status': 'Вы успешно отписались'},
                    status=status.HTTP_204_NO_CONTENT
                )
            except Subscription.DoesNotExist:
                raise ValidationError(
                    {'error': 'Вы не подписаны на этого пользователя'},
                    code=status.HTTP_400_BAD_REQUEST
                )
