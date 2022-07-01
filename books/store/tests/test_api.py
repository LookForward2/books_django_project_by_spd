import json
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
import rest_framework.status as status


from store.models import Book, UserBookRelation
from store.myserializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_username")
        self.book1 = Book.objects.create(
            name="Test Book 1", price=55,
            author_name='Author 1', owner=self.user)
        self.book2 = Book.objects.create(
            name="Test Book 2", price=100, author_name='Author 1')
        self.book3 = Book.objects.create(
            name="Test Book 3", price=30, author_name='Author 3')
        self.book4 = Book.objects.create(
            name="Book 4 about Author 3", price=100, author_name='Author 4')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer(
            [self.book1, self.book2, self.book3, self.book4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 100})
        serializer_data = BooksSerializer(
            [self.book2, self.book4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author 3'})
        serializer_data = BooksSerializer(
            [self.book3, self.book4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BooksSerializer(
            [self.book3, self.book1, self.book2, self.book4], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Programming in Python 3",
            "price": 1499.95,
            "author_name": "Mark Summerfield"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(5, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "id": self.book1.id,
            "name": self.book1.name,
            "price": 300,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        #self.book1 = Book.objects.get(id=self.book1.id)
        self.book1.refresh_from_db()
        self.assertEqual(300, self.book1.price)

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username="test_username2")
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 300,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({
            'detail': ErrorDetail(
                string='You do not have permission to perform this action.',
                code='permission_denied')
        }, response.data)
        self.book1.refresh_from_db()
        self.assertEqual(55, self.book1.price)

    def test_update_staff(self):
        self.user2 = User.objects.create(
            username="test_username2", is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": 300,
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(300, self.book1.price)

    def test_delete(self):
        self.assertEqual(4, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, Book.objects.all().count())

    def test_delete_not_owner(self):
        self.assertEqual(4, Book.objects.all().count())
        self.user2 = User.objects.create(username="test_username2")
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({
            'detail': ErrorDetail(
                string='You do not have permission to perform this action.',
                code='permission_denied')
        }, response.data)
        self.assertEqual(4, Book.objects.all().count())

    def test_delete_staff(self):
        self.assertEqual(4, Book.objects.all().count())
        self.user2 = User.objects.create(
            username="test_username2", is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(3, Book.objects.all().count())


class BooksRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_username")
        self.user2 = User.objects.create(username="test_username2")
        self.book1 = Book.objects.create(
            name="Test Book 1", price=55,
            author_name='Author 1', owner=self.user)
        self.book2 = Book.objects.create(
            name="Test Book 2", price=100,
            author_name='Author 1', owner=self.user2)

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        # "patch" looks like "put" but only one field
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user, book=self.book1)
        self.assertTrue(relation.like)

    def test_inbookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        # "patch" looks like "put" but only one field
        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user, book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_like_and_inbookmarks(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user, book=self.book1)
        self.assertTrue(relation.like)

        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user, book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data = {
            "rate": 5,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        # "patch" looks like "put" but only one field
        response = self.client.patch(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user, book=self.book1)
        self.assertEqual(5, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))
        data = {
            "rate": 8,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        # "patch" looks like "put" but only one field
        response = self.client.patch(
            url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
        expected = {'rate': [ErrorDetail(string='"8" is not a valid choice.', code='invalid_choice')]}
        self.assertEqual(expected, response.data)
        relation = UserBookRelation.objects.get(
            user=self.user, book=self.book1)
        self.assertEqual(None, relation.rate)