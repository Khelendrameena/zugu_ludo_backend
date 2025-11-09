from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GameRoomViewSet,
    WalletViewSet,
    TournamentViewSet,
    LeaderboardViewSet,
    GameStatsView
)

router = DefaultRouter()
router.register(r'rooms', GameRoomViewSet, basename='gameroom')
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'tournaments', TournamentViewSet, basename='tournament')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', GameStatsView.as_view(), name='game-stats'),
]
