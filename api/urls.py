# myapp/urls.py

from django.urls import path, include
from .views import WorldViewSet
from rest_framework.routers import DefaultRouter
from api import views


router = DefaultRouter()
router.register(r'world', views.WorldViewSet)
router.register(r'character', views.CharacterViewSet)
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
router.register(r'SavedGameState', views.SavedGameStateViewSet)



urlpatterns = [
    #path('world', WorldView.as_view()),
    path('', include(router.urls)),
    # Autres URL...

]

