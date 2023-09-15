from django.db import models

# Create your models here.

class Tag(models.Model):
    caption = models.CharField(max_length=20, default="new tag", unique=True, db_index=True)

class Author(models.Model):
    first_name = models.CharField(max_length=50, unique=True, db_index=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()

class Post(models.Model):
    title = models.CharField(max_length=100)
    image_name = models.CharField(max_length=100)
    date = models.DateField(auto_now=True)
    post = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag)