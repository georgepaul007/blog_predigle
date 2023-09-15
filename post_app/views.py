from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView, Response
from .models import Post, Author, Tag
from rest_framework.decorators import api_view
from .serializers import PostSerializer, AuthorSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
@swagger_auto_schema(
    method='POST',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'content': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
            'tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        },
        required=['title', 'content', 'author'],
    ),
    responses={200: 'Post created successfully', 400: 'Bad Request'},
)
@api_view(['POST'])
def create_post(request, slug):
    print(request.data)
    title = request.data.get('title')
    content = request.data.get('content')
    author = request.data.get('author')
    author_of_post = get_object_or_404(Author, first_name=author)
    current_author = AuthorSerializer(author_of_post).data
    tags = request.data.get('tags', [])
    post = Post.objects.create(title=title, post=slug,content=content, author=author_of_post)
    for tag_caption in tags:
        tag = get_object_or_404(Tag, caption=tag_caption)
        post.tags.add(tag)
    response_data = {"response": "post-created"}
    return Response(response_data,status=status.HTTP_200_OK)

    
@api_view(['GET'])
def get_posts(request):
    data = Post.objects.all()
    post_data = PostSerializer(data, many=True).data
    response_data = {"data": post_data}
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_three_posts(request):
    data = Post.objects.all().order_by("-date")[:3]
    post_data = PostSerializer(data, many=True).data
    response_data = {"data": post_data}
    return Response(response_data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='PUT',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'content': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
            'tags': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
        },
        required=['title', 'content', 'author'],
    ),
    responses={200: 'Post created successfully', 400: 'Bad Request'},
)
@api_view(['PUT'])
def update_post(request, slug):
    data = Post.objects.filter(post=slug).first
    if data is None: 
        return Response({"data": "Post was not present"}, status=status.HTTP_404_NOT_FOUND)
    data.title = request.data.get('title')
    data.content = request.data.get('content')
    print(request.data)
    author_of_post = Author.objects.get(first_name=request.data.get('author'))
    current_author = AuthorSerializer(author_of_post).data
    tags = request.data.get('tags', [])
    data.author = current_author
    data.tags = tags
    response_data = {"response": "post-updated"}
    return Response(response_data,status=status.HTTP_200_OK)
