from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate

from .models import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.db import IntegrityError
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


class Register(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.create( username=request.data['username'],
                                       grade=request.data['grade'],
                                       school=request.data['school'],
                                       email=request.data['email'],
                                       major=request.data['major'],
                                       project=request.data['project'],
                                       password=request.data['password'],
                                       start_date=request.data['start_date'],
                                       end_date=request.data['end_date'])
            user.set_password(request.data['password'])
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except IntegrityError as e:
            return Response({"ERROR": str(e)}, status=400)
        
class Login(APIView):
    def post(self, request, *args, **kwargs):
        user = authenticate(email=request.data['email'], password=request.data['password'])
        if user is None:
            return Response({'result': 'login fail'})
        else:
            token = TokenObtainPairSerializer.get_token(user)
            return Response({
                'refresh_token': str(token),
                'access_token': str(token.access_token),
                'user_id': user.id,
            })

class SearchUser(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        username = data.get('username')
        grade = data.get('grade')
        school = data.get('school')
        email = data.get('email')
        major = data.get('major')
        project = data.get('project')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if username:
            user = User.objects.filter(username=username)
        elif grade:
            user = User.objects.filter(grade=grade)
        elif school:
            user = User.objects.filter(school=school)
        elif email:
            user = User.objects.filter(email=email)
        elif major:
            user = User.objects.filter(major=major)
        elif project:
            user = User.objects.filter(project=project)
        
        else:
            user = User.objects.all()

        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)
    
class CreatePostView(APIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id = request.data['id'])
        try:
            post = Post.objects.create(title=request.data['title'],
                                       content=request.data['content'],
                                       category=request.data['category'],
                                       user=user)
            post.save()
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except IntegrityError as e:
            return Response({"ERROR": str(e)})

class ReadPostView(APIView):
    def get(self, request, *args, **kwargs):
        data = request.data
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        user = data.get('user')
        
        if title:
            post = Post.objects.filter(title=title)
        elif content:
            post = Post.objects.filter(content=content)
        elif category:
            post = Post.objects.filter(category=category)
        elif user:
            post = Post.objects.filter(user=User.objects.get(id = user))
        else:
            post = Post.objects.all()
        serializer = PostSerializer(post, many=True)
        return Response(serializer.data)

class UpdatePostView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id')

        post = Post.objects.get(id=id)
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        
        if title:
            post.title = title
        elif content:
            post.content = content
        elif category:
            post.category = category

        post.save()
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
class DeletePostView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id')
        post = Post.objects.get(id=id)
        post.delete()
        return Response({'result': 'delete success'})

class PostDetailView(APIView):
    def get(self, request, id, *args, **kwargs):
        post = Post.objects.filter(id=id).first()
        comments = Comment.objects.filter(post=post)
        user = User.objects.filter(id=post.user.id).first()
        serializer = PostCommentSerializer({"user": user, "post" : post, "comment" : comments})
        return Response(serializer.data)
    
class MatchingUserView(APIView):
    def get(self, request, *args, **kwargs):
        data = request.data
        project = data.get('project')
        major = data.get('major')

        users = User.objects.filter(project=project, major=major)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
class DetailUserView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id')

        user = User.objects.filter(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class UserProfileView(APIView):
    def get(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id')

        user = User.objects.get(id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class UpdateUserProfileView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        major = data.get('major')
        project = data.get('project')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        id = data.get('id')
        user = User.objects.get(id=id)
        user.major = major
        user.project = project
        user.start_date = start_date
        user.end_date = end_date
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
class CreateCommentView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        content = data.get('content')
        post = Post.objects.get(id = data.get('post_id'))
        user = User.objects.get(id = data.get('user_id'))

        comment = Comment.objects.create(content=content, post=post, user=user)
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
class UpdateCommentView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        comment = Comment.objects.get(id = data.get('id'))
        content = data.get('content')

        comment.content = content
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
class DeleteCommentView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        comment = Comment.objects.get(id = data.get('id'))
        comment.delete()
        return Response({'result': 'delete success'})