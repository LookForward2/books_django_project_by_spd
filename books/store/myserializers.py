from dataclasses import fields
#from django.forms import IntegerField
from rest_framework.serializers import ModelSerializer, SerializerMethodField, IntegerField
from store.models import Book, UserBookRelation


class BooksSerializer(ModelSerializer):
    likes_count = SerializerMethodField() # Annotate LES_8
    annotated_likes = IntegerField() # Annotate LES_8

    class Meta:
        model = Book
        # fields = '__all__'
        fields = ('id', 'name', 'price', 'author_name', 'likes_count', 'annotated_likes')
    
    def get_likes_count(self, instance):
        # Annotate LES_8
        return UserBookRelation.objects.filter(book=instance, like=True).count()

class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ('book', 'like', 'in_bookmarks', 'rate')
