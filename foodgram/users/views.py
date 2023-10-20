from django.shortcuts import render
from .models import User, Subscribe
from rest_framework import viewsets
from .serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['post'], detail=True, url_path='subscribe')
    def subscribe(self, request, pk):
        current_user = request.user
        who_to_follow = User.objects.filter(id=pk)
        Subscribe.objects.create(user=current_user, author=who_to_follow)
        serializer = UserSerializer(who_to_follow)
        return Response(serializer.data)
