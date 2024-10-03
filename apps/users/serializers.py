"""
DRF Serializers for Users API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["bio", "location", "birth_date", "profile_picture", "is_email_verified"]
        read_only_fields = ["is_email_verified"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source="userprofile", read_only=True)
    total_reviews = serializers.SerializerMethodField()
    total_books_read = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "date_joined", "profile", "total_reviews", "total_books_read"
        ]
        read_only_fields = ["id", "date_joined"]
    
    def get_total_reviews(self, obj):
        return obj.book_reviews.filter(is_approved=True).count()
    
    def get_total_books_read(self, obj):
        from apps.reading_lists.models import ShelfBook
        return ShelfBook.objects.filter(
            shelf__user=obj,
            shelf__name__iexact="read"
        ).count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ["username", "email", "password", "password_confirm", "first_name", "last_name"]
    
    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source="userprofile")
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile"]
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("userprofile", None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data:
            profile = instance.userprofile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance

