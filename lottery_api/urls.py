from django.urls import path, include
from rest_framework.routers import DefaultRouter
from lottery_api import views

# ModelViewSetを継承して作ったViewはrouterに追加できるけどgenericsを使ったViewはurlpatternsに書き足していく
app_name = 'api'

router = DefaultRouter()
router.register('profile', views.ProfileViewSet)
# 同じシリアライザーを参照している場合は第3引数にbasenameを明示的につけないといけない
router.register('message', views.MessageViewSet, basename='message')
router.register('inbox', views.InboxListView, basename='inbox')  # 自分が送信したメッセージを返す

# 汎用のAPIView（generics.〜）で作ったものはurlpatternsに書いていく
urlpatterns = [
    path('miniloto/', views.MiniLotoListView.as_view(), name='miniloto'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('myprofile/', views.MyProfileListView.as_view(), name='myprofile'),
    path('', include(router.urls))
]
