from django.contrib import admin
from .models import Post, PostType, Profile, Comment

# Register your models here.
admin.site.register(Post)
admin.site.register(PostType)

admin.site.register(Profile)
admin.site.register(Comment)


