from django.shortcuts import get_object_or_404, redirect, render
from tagrebte.models import Comment, Post, PostType
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import PostCreateForm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from tagrebte.forms import NewComment
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserCreationForm, ProfileUpdateForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from .filters import TypeFilter
from .api import PostAPI, UserAPI , CommentsAPI
from rest_framework import viewsets


def types(request):

    type = PostType.objects.all()
    post = Post.objects.all()[0:5]

    myfilter = TypeFilter(request.GET, queryset= type)
    type = myfilter.qs
    
    
    paginator = Paginator(type, 30)
    page = request.GET.get('page')
    try:
        type = paginator.page(page)
    except PageNotAnInteger:
        type = paginator.page(1)
    except EmptyPage:
        type = paginator.page(paginator.num_pages)

    




    return render(request, 'types.html', {'title':'الرئيسية','type':type, 'myfilter':myfilter,'page': page,'post':post})
    

def index(request, id):
    post = Post.objects.filter( post_type = id)
    type = PostType.objects.filter( id = id).first()  

         
    # print()
   

    if request.method == 'POST':
        post_form = PostCreateForm(data=request.POST)     
        if post_form.is_valid():         
            new_post = post_form.save(commit=False)        
            new_post.owner = request.user
            new_post.post_type = type 
            PostType.objects.filter( id = id).update(post_count= type.post_count + 1 )
            new_post.save()      
            post_form.is_valid = False
            post_form = PostCreateForm()

    else:
       
        post_form = PostCreateForm()


    paginator = Paginator(post, 5)
    page = request.GET.get('page')


    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)
  
    # post = Post.objects.filter( post_type = 3)
    return render(request, 'index.html', {'title':type,'post':post,'page': page,'form':post_form})

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        comment_form = NewComment(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            first_name = request.user.first_name
            last_name = request.user.last_name
            name = first_name +" "+ last_name
            new_comment.name = name
            new_comment.save()
            comment_form.is_valid = False
            comment_form = NewComment()


    else:
        comment_form = NewComment()

    context = {
         'title': "تفاصيل",
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    }

    return render(request, 'detail.html', context)

class PostUpdateView(UserPassesTestMixin, LoginRequiredMixin, UpdateView):      





    model = Post
    template_name = 'post_update.html'
    form_class = PostCreateForm


    def get_context_data(self, **kwargs):  #more than one context  [sea list.html]
        context = super().get_context_data(**kwargs)
        context['title'] =  'تحرير'
       
        return context
    

    def form_valid(self, form):
        form.instance.owner = self.request.user
        

        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        else:
            return False


class PostDeleteView(UserPassesTestMixin, LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'post_confirm_delete.html'


    def get_context_data(self, **kwargs):  #more than one context  [sea list.html]
        context = super().get_context_data(**kwargs)
        context['title'] =  'حذف'
       
        return context

    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        post = self.get_object()
        type = PostType.objects.filter( id = post.post_type.id).first()  
        PostType.objects.filter( id = post.post_type.id).update(post_count= type.post_count - 1 )
        self.object.delete()
        return HttpResponseRedirect(success_url+str(post.post_type.id))
     
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


def delete_own_comment(request, comment_id,post_id):
    comment = Comment.objects.get(pk=comment_id)
    post = Post.objects.get( pk=post_id )
    comment.delete()
    return redirect('detail/'+str(post_id))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            # username = form.cleaned_data['username']
            new_user.set_password(form.cleaned_data['password1'])
            new_user.save()
            messages.success(request, 'تهانينا {} لقد تمت عملية التسجيل بنجاح.'.format(new_user))
            # messages.success(
            #     request, f'تهانينا {username} لقد تمت عملية التسجيل بنجاح . ')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {
        'title': 'التسجيل',
        'form': form,
    })


def login_user(request):
    if request.method == 'POST':
        # form = LoginForm()
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.warning(request, 'هناك خطأ في اسم المستخدم او كلمة المرور')

    # else:
    #     form = LoginForm()
    return render(request, 'login.html', {
        'title': 'تسجيل الدخول',
        # 'form': form,

    })


def logout_user(request):
    logout(request)
    return render(request, 'logout.html', {
        "title": 'تسجيل الخروج'})


@login_required(login_url='login')
def profile(request):
    posts = Post.objects.filter(owner=request.user)
    post_list = Post.objects.filter(owner=request.user)
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')
    exp_num =  Post.objects.filter(owner=request.user , mytype='تجربة').count()
    que_num =  Post.objects.filter(owner=request.user,  mytype='استفسار').count()
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)

    return render(request, 'profile.html', {
        "title": "الملف الشخصي",
        "posts": posts,
        'page': page,
        'que_num': que_num,
        'exp_num': exp_num,
        'post_list': post_list,
    })


@login_required(login_url='login')
def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'تم تحديث الملف الشخصي.')
            return redirect('profile')


    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'title': 'تعديل الملف الشخصي',
        'user_form': user_form,
        'profile_form': profile_form,

    }

    return render(request, "profile_update.html", context)


def about(request):
    return render(request, 'about.html', {'title': 'عن الموقع '})





#api

class Post_api(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostAPI

class User_api(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserAPI

class Comments_api(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentsAPI
    
