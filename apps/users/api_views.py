"""
REST API ViewSets for Users
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.core.cache import cache

from apps.users.serializers import (
    UserSerializer, UserRegistrationSerializer, UserUpdateSerializer
)
from apps.books.serializers import BookReviewSerializer
from apps.reading_lists.models import ReadingShelf


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user operations.
    """
    queryset = User.objects.select_related("profile").all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer
    
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """Get all reviews by a user"""
        user = self.get_object()
        reviews = user.book_reviews.filter(is_approved=True).select_related("book")
        serializer = BookReviewSerializer(reviews, many=True, context={"request": request})
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def shelves(self, request, pk=None):
        """Get user's reading shelves"""
        user = self.get_object()
        shelves = ReadingShelf.objects.filter(user=user)
        
        if user != request.user:
            shelves = shelves.filter(is_public=True)
        
        data = []
        for shelf in shelves:
            data.append({
                "id": shelf.id,
                "name": shelf.name,
                "is_public": shelf.is_public,
                "book_count": shelf.get_book_count(),
                "created_at": shelf.created_at
            })
        
        return Response(data)
    
    @action(detail=False, methods=["patch"], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

