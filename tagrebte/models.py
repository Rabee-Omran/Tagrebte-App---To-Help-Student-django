from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from PIL import Image

# Create your models here
class PostType(models.Model):
    types = models.CharField(max_length=40)
    post_count = models.IntegerField(default=0 , blank=True, null=True)
  
   
    def __str__(self):
        return self.types


POST_TYPE = (
    ('تجربة', 'تجربة'),
    ('استفسار', 'استفسار'),
)

class Post(models.Model):
    owner = models.ForeignKey(User, related_name='job_owner', on_delete=models.CASCADE,)
    content = models.TextField(max_length=8000)
    post_type = models.ForeignKey(PostType, related_name='post_type', on_delete=models.CASCADE,blank=True, null=True)
    published_at = models.DateTimeField(auto_now=True)
    mytype = models.CharField(max_length=15, choices=POST_TYPE,blank=True, null=True) 
   

   
    def __str__(self):
        return self.owner.username
    class Meta:
        ordering = ('-published_at',)
    
    def get_absolute_url(self):
        #return '/detail/{}'.format(self.pk)
        return reverse('detail', args=[self.pk])



class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,blank=True, null=True, related_name='user')
    name = models.CharField(max_length=50, verbose_name='الأسم')
    body = models.TextField(verbose_name="التعليق/الاستفسار")
    comment_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return 'علق {} على {}.'.format(self.name, self.post)

    class Meta:
        ordering = ('-comment_date',)


class Profile(models.Model):
    image = models.ImageField(default='unnamed.png', upload_to='profile_pics')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return '{} profile'.format(self.user.username)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.width > 300 or img.height > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)



def create_profile(sender, **kwarg):
    if kwarg['created']:
        Profile.objects.create(user=kwarg['instance'])


post_save.connect(create_profile, sender=User)





  


  



  
