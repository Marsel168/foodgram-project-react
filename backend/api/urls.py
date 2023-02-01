from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .v1.views import (CustomUserViewSet, FollowListView, FollowView,
                       IngredientViewSet, RecipeViewSet, TagViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'users', CustomUserViewSet, basename='users')

auth_urls = [
    path('token/login/', TokenCreateView.as_view()),
    path('token/logout/', TokenDestroyView.as_view()),
]

users_urls = [
    path('users/subscriptions/',
         FollowListView.as_view(), name='subscription'),
    path('users/<int:user_id>/subscribe/',
         FollowView.as_view(), name='subscribe'),
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('users', include(users_urls)),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls'))
]
