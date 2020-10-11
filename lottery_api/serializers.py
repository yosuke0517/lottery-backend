from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from lottery_api.models import Profile, Message, MiniLoto


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # ↓はmodelって名前じゃないとエラーになる
        model = get_user_model()
        # フロントへ返却されるフィールド
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    # トークンを生成して保存するようにオーバーライド
    def create(self, validated_date):
        # ユーザ生成（↑でpasswordをwrite_onlyにしているのでフロントへ返すレスポンスとしてはidとemailになる
        user = get_user_model().objects.create_user(**validated_date)
        # トークン保存
        Token.objects.create(user=user)
        # TODO Trialも更新するようにする
        return user


class ProfileSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        # ↓はmodelって名前じゃないとエラーになる
        model = Profile
        # フロントへ返却されるフィールド
        fields = ('id', 'nickName', 'user', 'created_on', 'img')
        # ログインユーザのuserProを入れるようにする
        extra_kwargs = {'user': {'read_only': True}}


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        # ↓はmodelって名前じゃないとエラーになる
        model = Message
        # フロントへ返却されるフィールド
        fields = ('id', 'sender', 'content')
        # ログインしているユーザをsenderにする
        extra_kwargs = {'sender': {'read_only': True}}


class MiniLotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiniLoto
        fields = ('lottery_date', 'times', 'number_1', 'number_2', 'number_3', 'number_4'
                  , 'number_5', 'bonus_number1')
