#graphGEFXServer/api/urls.py


from django.urls import path, include, re_path
from .views import MyTokenObtainPairView
from rest_framework.routers import DefaultRouter
from api import views
from rest_framework_simplejwt.views import (
    TokenRefreshView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Documentation de l'API",
        default_version='v1',
        description="Description détaillée de l'API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@monapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'world', views.WorldViewSet)
router.register(r'character', views.CharacterViewSet)
router.register(r'characterclass', views.CharacterClassViewSet, basename='characterclass')
router.register(r'skill', views.SkillViewSet)
router.register(r'characterskill', views.CharacterSkillViewSet)
router.register(r'item', views.ItemViewSet)
router.register(r'characterinventory', views.CharacterInventoryViewSet)
router.register(r'tile', views.TileViewSet)
router.register(r'monster', views.MonsterViewSet)
router.register(r'shop', views.ShopViewSet)
router.register(r'shopitem', views.ShopItemViewSet)
router.register(r'chest', views.ChestViewSet)
router.register(r'chestitem', views.ChestItemViewSet)



urlpatterns = [
    #path('world', WorldView.as_view()),
    path('', include(router.urls)),
    # Autres URL...
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('character/start_new_game/', views.CharacterViewSet.as_view({'post': 'start_new_game'}), name='start-new-game'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]

