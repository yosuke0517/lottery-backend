from rest_framework import permissions


class ProfilePermission(permissions.BasePermission):
    # アクセスしてきたユーザのidがログインしているユーザのidと同じ場合のみ更新等ができるようにする
    def has_object_permission(self, request, view, obj):
        # セーフメソッドは問答無用でOK
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user.id == request.user.id