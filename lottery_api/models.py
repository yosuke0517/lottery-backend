import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


# アップロードされたファイルを正規化する
def upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['image', str(instance.user.id) + str(instance.nickName) + str(".") + str(ext)])


"""
認証はデフォルトだとユーザ名とパスワードなのでemail他に変更したい場合はオーバーライドが必要になる
"""


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    # スーパーユーザを作成するならコチラもオーバーライド
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


"""
コチラも上記と同様にオーバーライド
"""


class User(AbstractBaseUser, PermissionsMixin):
    """ユーザ"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField('ユーザ名', max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Trial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 認証用ユーザと紐付け
    user = models.OneToOneField(User, related_name='trialUser', on_delete=models.CASCADE)
    is_tried = models.BooleanField(default=False)
    # ユーザ作成と同時にトライアル開始とする
    is_trying = models.BooleanField(default=True)
    # ユーザ作成と同時にトライアル開始とする
    start_at = models.DateTimeField(auto_now_add=True)
    end_at = models.DateTimeField(auto_now_add=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.id


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 認証用ユーザと紐付け
    user = models.OneToOneField(User, related_name='userProf', on_delete=models.CASCADE)
    nickName = models.CharField(max_length=20)
    introduction = models.CharField(max_length=255)
    img = models.ImageField(blank=True, null=True, upload_to=upload_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickName


# class FriendRequest(models.Model):
#     askFrom = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='askFrom', on_delete=models.CASCADE)
#     askTo = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='askTo', on_delete=models.CASCADE)
#
#     # 許可したかどうか
#     approved = models.BooleanField(default=False)
#
#     # ユニークになるように制約をかける
#     class Meta:
#         unique_together = (('askFrom', 'askTo'),)
#
#     # from to を表示するようにする
#     def __str__(self):
#         return str(self.askFrom) + '------->' + str(self.askTo)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=255)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sender


class MiniLoto(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=20)
    lottery_date = models.DateTimeField(auto_now_add=True)
    times = models.IntegerField()
    number_1 = models.CharField(max_length=20)
    number_2 = models.CharField(max_length=20)
    number_3 = models.CharField(max_length=20)
    number_4 = models.CharField(max_length=20)
    number_5 = models.CharField(max_length=20)
    bonus_number1 = models.CharField(max_length=20)
    lottery_number = models.CharField(max_length=50)


class LotoSix(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=20)
    lottery_date = models.DateTimeField(auto_now_add=True)
    times = models.IntegerField()
    number_1 = models.CharField(max_length=20)
    number_2 = models.CharField(max_length=20)
    number_3 = models.CharField(max_length=20)
    number_4 = models.CharField(max_length=20)
    number_5 = models.CharField(max_length=20)
    number_6 = models.CharField(max_length=20)
    bonus_number1 = models.CharField(max_length=20)
    lottery_number = models.CharField(max_length=50)


class LotoSeven(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=20)
    lottery_date = models.DateTimeField(auto_now_add=True)
    times = models.IntegerField()
    number_1 = models.CharField(max_length=20)
    number_2 = models.CharField(max_length=20)
    number_3 = models.CharField(max_length=20)
    number_4 = models.CharField(max_length=20)
    number_5 = models.CharField(max_length=20)
    number_6 = models.CharField(max_length=20)
    number_7 = models.CharField(max_length=20)
    bonus_number1 = models.CharField(max_length=20)
    bonus_number2 = models.CharField(max_length=20)
    lottery_number = models.CharField(max_length=50)
