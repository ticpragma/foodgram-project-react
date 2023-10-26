from djoser.views import UserViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated


class DjoserUserViewSet(UserViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]

    def me(self, request, *args, **kwargs):
        response = super().me(request, *args, **kwargs)
        response.data['is_subscribed'] = False
        return response
