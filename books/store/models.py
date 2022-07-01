from pyexpat import model
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')
    # isbn = models.CharField('ISBN', max_length=13, unique=True,
    #                          help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    def __str__(self):
        return self.name

class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, "Ok"),
        (2, "Good"),
        (3, "Fine"),
        (4, "Amazing"),
        (5, "Awesome"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user} thinks {self.book.name} is {self.RATE_CHOICES[self.rate-1][1]}' 