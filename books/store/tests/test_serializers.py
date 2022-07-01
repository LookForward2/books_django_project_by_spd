from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Count, Case, When

from store.models import Book, UserBookRelation
from store.myserializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="test_username1")
        self.user2 = User.objects.create(username="test_username2")
        self.user3 = User.objects.create(username="test_username3")
        self.book1 = Book.objects.create(
            name="Test Book 1", price='55.95', author_name='Author 1', owner=self.user1)
        self.book2 = Book.objects.create(
            name="Test Book 2", price='100.75', author_name='Author 2', owner=self.user1)

        UserBookRelation.objects.create(
            user=self.user1, book=self.book1, like=True)
        UserBookRelation.objects.create(
            user=self.user2, book=self.book1, like=True)
        UserBookRelation.objects.create(
            user=self.user3, book=self.book1, like=True)

        UserBookRelation.objects.create(
            user=self.user1, book=self.book2, like=False)
        UserBookRelation.objects.create(
            user=self.user2, book=self.book2, like=True)
        UserBookRelation.objects.create(
            user=self.user3, book=self.book2, like=True)

    def test_ok(self):
        books = Book.objects.all().annotate(annotated_likes=Count(
            Case(When(userbookrelation__like=True, then=1)))).order_by('id') 
            # order_by() - it messes the order so test fails
        serializer_data = BooksSerializer(books, many=True).data
        # serializer_data = BooksSerializer([self.book1, self.book2], many=True).data
        expected_data = [
            {
                'id': self.book1.id,
                'name': "Test Book 1",
                'price': '55.95',
                'author_name': 'Author 1',
                # 'owner': self.user.id,
                'likes_count': 3,
                'annotated_likes': 3,
            },
            {
                'id': self.book2.id,
                'name': 'Test Book 2',
                'price': '100.75',
                'author_name': 'Author 2',
                # 'owner': self.user.id,
                'likes_count': 2,
                'annotated_likes': 2,
            }
        ]
        self.assertEqual(expected_data, serializer_data)
