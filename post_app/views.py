from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView, Response
from .models import Post, Author, Tag
from rest_framework.decorators import api_view
from .serializers import PostSerializer, AuthorSerializer, CreatePostSerializer, TagSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q


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
    if Post.objects.filter(post=slug).exists():
        return Response({"response": "Post with slug already exists"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = CreatePostSerializer(data=request.data)
    if serializer.is_valid():
        author_name = serializer.validated_data['author']
        if not Author.objects.filter(first_name=author_name).exists():
            return Response({"response": "Author does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        author_of_post = Author.objects.get(first_name=author_name)
        tags = serializer.validated_data.get('tags', [])
        tag_objects = []
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(caption=tag_name)
            tag_objects.append(tag)

        serializer.validated_data['author'] = author_of_post
        serializer.validated_data.pop('tags')
        post = Post.objects.create(post=slug,  **serializer.validated_data)
        post.tags.set(tag_objects)
        response_data = {"response": "post-created"}
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def get_posts(request):
    data = Post.objects.all()
    post_data = PostSerializer(data, many=True).data
    for post in post_data:
        tag_objects = []
        for tag in post['tags']:
            tag_objects.append(Tag.objects.get(id=tag))
        print(tag_objects)
        post['tags'] = TagSerializer(tag_objects, many=True).data
        author_id = post['author']
        author = Author.objects.get(id=author_id)
        post['author'] = AuthorSerializer(author).data 
    response_data = {"data": post_data}
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_three_posts(request):
    data = Post.objects.all().order_by("-date")[:3]
    post_data = PostSerializer(data, many=True).data
    for post in post_data:
        tag_objects = []
        for tag in post['tags']:
            tag_objects.append(Tag.objects.get(id=tag))
        print(tag_objects)
        post['tags'] = TagSerializer(tag_objects, many=True).data
        author_id = post['author']
        author = Author.objects.get(id=author_id)
        post['author'] = AuthorSerializer(author).data
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
    data = Post.objects.filter(post=slug).first()
    if data is None: 
        return Response({"data": "Post was not present"}, status=status.HTTP_404_NOT_FOUND)
    data.content = request.data.get('content')
    data.title = request.data.get('title')
    print(request.data)
    author_of_post = Author.objects.get(first_name=request.data.get('author'))
    tags = request.data.get('tags', [])
    tag_objects = []
    for tag_name in tags:
        tag, created = Tag.objects.get_or_create(caption=tag_name)
        tag_objects.append(tag)

    data.tags.set(tag_objects)
    data.author = author_of_post
    data.save()
    if(created):
        response_data = {"response": "post updated, new tag created"}
    response_data = {"response": "post-updated"}
    return Response(response_data,status=status.HTTP_200_OK)

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
def get_by_filter(request):
    title = request.data.get('title')
    content = request.data.get('content')
    author = request.data.get('author')
    tags = request.data.get('tags')
    print(title, " ", content, " ", author, " ", tags, "")
    query = Q()

    if title:
        query &= Q(title__exact=title)
    if content:
        query &= Q(content=content)
    if author:
        query &= Q(author__first_name=author)
    if tags:
        query &= Q(tags__caption__in=tags)

    filtered_posts = Post.objects.filter(query)

    serializer = PostSerializer(filtered_posts, many=True)

    return Response(serializer.data)


@api_view(['DELETE'])
def delete_post(request, slug):
    try:
        post = Post.objects.get(post=slug)
    except Post.DoesNotExist:
        return Response({"message": f"Post with name '{slug}' does not exist."}, status=status.HTTP_404_NOT_FOUND)

    post.delete()
    return Response({"message": f"Post '{slug}' has been deleted."}, status=status.HTTP_204_NO_CONTENT)
