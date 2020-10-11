from rest_framework import authentication, permissions, generics
from lottery_api import serializers, custompermissions
from lottery_api.models import Message, Profile, MiniLoto
from django.db.models import Q
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response


class CreateUserView(generics.CreateAPIView):
    # ユーザの新規作成に関するviewはコレだけ（serializer_classに対象のシリアライザーを入れる）
    serializer_class = serializers.UserSerializer


# ModelViewSetはオーバーライドしなければCRUD全て使えてしまうので使わせたくないなら非アクティベートしないといけない
# 自分以外が送信したメッセージを取得
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = serializers.MessageSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # GET時自分以外が送信したメッセージを取得
    def get_queryset(self):
        return self.queryset.exclude(Q(sender=self.request.user))

    # CREATE時のsenderは常にログインユーザ
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    # 削除・更新はしないのでエラーを返す
    def destroy(self, request, *args, **kwargs):
        response = {'message': 'Delete DM is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        response = {'message': 'Update DM is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        response = {'message': 'Patch DM is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


# 自分が送信したメッセージのみ返してあげる
class InboxListView(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = serializers.MessageSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    # GET時自分が送信したメッセージのみ返してあげる
    def get_queryset(self):
        return self.queryset.filter(sender=self.request.user)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    # 認証済みかつ、自作したパーミッションがOKの場合のみ
    permission_classes = (permissions.IsAuthenticated, custompermissions.ProfilePermission)

    def perform_create(self, serializer):
        # ログインユーザとuserProを紐付ける
        serializer.save(user=self.request.user)


# 汎用APIView ListAPIView （リストを取得するだけの用途）他にもCreateAPIViewとかがある
class MyProfileListView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


# 汎用APIView ListAPIView （リストを取得するだけの用途）他にもCreateAPIViewとかがある
class MiniLotoListView(generics.ListAPIView):
    queryset = MiniLoto.objects
    serializer_class = serializers.MiniLotoSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset
