from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import TemplateView, View
from .forms import RegistForm, UserLoginForm, ProfileForm, AnalysisPeriodForm, CommentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from .models import Post, Connection
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from . import models
from . import graph
from django.db.models import Count
import pandas as pd
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from .models import Post, Notification, Comment
from dateutil.relativedelta import relativedelta

class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm

# class UserLoginView(FormView):
#     template_name = 'user_login.html'
#     form_class = UserLoginForm

#     def post(self, request, *args, **kwargs):
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(email=email, password=password)
#         next_url = request.POST['next']
#         if user is not None and user.is_active:
#             login(request, user)
#         if next_url:
#             return redirect(next_url)
#         return redirect('accounts:home')

class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(1209600)
        return super().form_valid(form)
    

# class UserLogoutView(View):
    
#     def get(self, request, *args, **kwargs):
#         logout(request)
#         return redirect('accounts:user_login')

class UserLogoutView(LogoutView):
    pass
    
class MyView(LoginRequiredMixin, TemplateView): #LoginRequiredMixin
    template_name = "mypage.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ピン止めされた投稿を取得してコンテクストに追加
        context['pinned_post'] = Post.objects.filter(pinned=True).first()
        return context
    

class FriendPostView(LoginRequiredMixin, ListView): #LoginRequiredMixin
    #friendpostページで、自分以外のユーザー投稿をリスト表示
    model = Post
    template_name = 'friendpost.html'

    def get_queryset(self):
        #リクエストユーザーのみ除外
        return Post.objects.exclude(user=self.request.user)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #get_or_createにしないとサインアップ時オブジェクトがないためエラーになる
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context
    
    

class MyPostView(LoginRequiredMixin, ListView): 
    #自分の投稿のみ表示
    model = Post
    template_name = 'mypost.html'
    
    def get_queryset(self):
        #自分の投稿に限定
        return Post.objects.filter(user=self.request.user)
    
    
class DetailPostView(LoginRequiredMixin, DetailView): 
    model = Post
    template_name = 'detail.html'
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context
    

class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'create.html'
    fields = ['date','title', 'image', 'content']
    success_url = reverse_lazy('accounts:mypost')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def newBook(self, request):
        if request.method == "POST":
            title = request.POST.get('title')
            image = request.FILES.get('image')
            content = request.POST.get('content')
            if title and image:
                post = Post.objects.create(
                    title=title,
                    image=image,
                    content=content,
                    user=request.user
                )
                return redirect('accounts:detail', pk=post.pk)
        else:
            return render(request, 'blog/new.html')

    # def create(request):
    # # リクエストのメソッドがPOSTなら
    # if request.method == 'POST':
    #     articleForm = ArticleForm(request.POST) # リクエストから取り出したデータを代入
    #     # 受け取ったデータが正常なら
    #     if articleForm.is_valid():
    #         article = articleForm.save() # データを保存
    # context = {
    #     'article': article,
    # }
    # return render(request, 'bbs/posted.html', context) # detail.htmlを返す
    

class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):   #LoginRequiredMixin
    model = Post
    template_name = 'update.html'
    fields = ['title', 'image', 'content']

    def get_success_url(self,  **kwargs):
        pk = self.kwargs["pk"]
        return reverse_lazy('accounts:detail', kwargs={"pk": pk})

    def test_func(self, **kwargs):       
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user) 

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'comment.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.post_id = self.kwargs['pk']
        post = Post.objects.get(pk=self.kwargs['pk'])
        related_post = Post.objects.get(pk=self.kwargs['pk'])
        Notification.objects.create(
            user=post.user,
            message=f"{self.request.user.username}が「{related_post.title}」にコメントしました。"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accounts:detail', kwargs={'pk': self.kwargs['pk']})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # コメント対象のオブジェクトを取得してコンテキストに追加
        context['object'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        return context


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): #LoginRequiredMixin
    #投稿編集ページ
    model = Post
    template_name = 'delete.html'
    success_url = reverse_lazy('accounts:mypost')

    def test_func(self, **kwargs):
        #アクセスできるユーザーを制限
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user) 
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        context['comment_form'] = CommentForm()
        return context
    

class LikeBase(LoginRequiredMixin, View): #LoginRequiredMixin
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        related_post = Post.objects.get(pk=pk)
        
        # if self.request.user in related_post.like.all(): 
        #     #テーブルからユーザーを削除 
        #     obj = related_post.like.remove(self.request.user)
        # #いいねテーブル内にすでにユーザーが存在しない場合
        # else:
        #     #テーブルにユーザーを追加                           
        #     obj = related_post.like.add(self.request.user)
        # return obj
        
        if self.request.user in related_post.like.all(): 
            related_post.like.remove(self.request.user)
        else:
            related_post.like.add(self.request.user)
            Notification.objects.create(
                user=related_post.user,
                message=f"{self.request.user.username}が「{related_post.title}」にいいねしました。"
            )
        return redirect('accounts:friendpost')
        

class LikeHomeView(LikeBase):
    #"""HOMEページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        #LikeBaseでリターンしたobj情報を継承
        super().get(request, *args, **kwargs)
        #homeにリダイレクト
        return redirect('accounts:friendpost')


class LikeDetailView(LikeBase):
    #"""詳細ページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        #LikeBaseでリターンしたobj情報を継承
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        #detailにリダイレクト
        return redirect('accounts:detail', pk)


class FollowBase(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        target_user = Post.objects.get(pk=pk).user
        my_connection = Connection.objects.get_or_create(user=self.request.user)
        
        if target_user in my_connection[0].following.all():
            my_connection[0].following.remove(target_user)
        else:
            my_connection[0].following.add(target_user)
            Notification.objects.create(
                user=target_user,
                message=f"{self.request.user.username}があなたをフォローしました。"
            )
        return redirect('accounts:friendpost')

class FollowHomeView(FollowBase):
    # """HOMEページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        #FollowBaseでリターンしたobj情報を継承
        super().get(request, *args, **kwargs)
        #homeにリダイレクト
        return redirect('accounts:friendpost')

class FollowDetailView(FollowBase):
    # """詳細ページでフォローした場合"""
    def get(self, request, *args, **kwargs):
        #FollowBaseでリターンしたobj情報を継承
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk'] 
        #detailにリダイレクト
        return redirect('accounts:detail', pk)

class FollowListView(LoginRequiredMixin, ListView): #LoginRequiredMixin
    #"""フォローしたユーザーの投稿をリスト表示"""
    model = Post
    template_name = 'friendpost.html'

    def get_queryset(self):
        #"""フォローリスト内にユーザーが含まれている場合のみクエリセット返す"""
        my_connection = Connection.objects.get_or_create(user=self.request.user)
        all_follow = my_connection[0].following.all()
        #投稿ユーザーがフォローしているユーザーに含まれている場合オブジェクトを返す。
        return Post.objects.filter(user__in=all_follow)

    def get_context_data(self, *args, **kwargs):
        #"""コネクションに関するオブジェクト情報をコンテクストに追加"""
        context = super().get_context_data(*args, **kwargs)
        #コンテクストに追加
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView): # 追加
    template_name = 'edit_profile.html'
    model = User
    form_class = ProfileForm
    success_url = '/accounts/edit_profile/'
    
    def get_object(self):
        return self.request.user

class PinPostView(View):
    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=self.kwargs['pk'])
        # ユーザーが自分の投稿かどうかを確認
        if post.user == request.user:
            # 元々ピン止めされていた投稿を取得
            pinned_post = Post.objects.filter(pinned=True, user=request.user).first()
            if pinned_post:
                # 元々ピン止めされていた投稿のピン止めを解除
                pinned_post.pinned = False
                pinned_post.save()

            # 新しい投稿をピン止め
            post.pinned = True
            post.save()
            return HttpResponseRedirect(reverse('accounts:detail', kwargs={'pk': post.pk}))
        else:
            return HttpResponseForbidden("You are not allowed to pin posts that are not yours.")

class UnpinPostView(View):
    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=self.kwargs['pk'])
        # ユーザーが自分の投稿かどうかを確認
        if post.user == request.user:
            # ピン止めされている投稿を取得してピン止め解除
            post.pinned = False
            post.save()
            return HttpResponseRedirect(reverse('accounts:detail', kwargs={'pk': post.pk}))
        else:
            return HttpResponseForbidden("You are not allowed to unpin posts that are not yours.")
        

class BookCountView(LoginRequiredMixin, TemplateView):
    template_name = "book_count.html"

    def get_context_data(self, **kwargs):
        qs    = models.Post.objects.filter(user=self.request.user)
        total_count = sum([post['count'] for post in qs.month_count()])
        x     = sorted([post['month'].strftime("%Y-%m") for post in qs.month_count()], reverse=True)
        y     = [post['count'] for post in qs.month_count()]
        chart = graph.Plot_Graph(x, y, y_max)

        context = super().get_context_data(**kwargs)
        context['chart'] = chart
        return context
    
    def get(self, request, *args, **kwargs):
        start_date = datetime.now() - timedelta(days=150)  # デフォルトは過去5カ月
        end_date = datetime.now() + relativedelta(months=1)
        
        if 'start_date' in request.GET and 'end_date' in request.GET:
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            start_date = datetime.strptime(start_date_str, "%Y-%m")
            end_date = datetime.strptime(end_date_str, "%Y-%m") + relativedelta(months=1)
            
            if start_date > end_date:
                error_message = "開始月と終了月が前後しています。"
                return render(request, self.template_name, {'error_message': error_message})
        
        posts = models.Post.objects.filter(user=request.user, date__range=[start_date, end_date + timedelta(days=1)])
        
        all_months = [start_date.strftime("%Y-%m")]
        current_date = start_date
        while current_date < end_date:
            all_months.append(current_date.strftime("%Y-%m"))
            current_date += relativedelta(months=1)

        x = all_months
        total_count = sum([post['count'] for post in posts.month_count()])
        y = [next((post['count'] for post in posts.month_count() if post['month'].strftime("%Y-%m") == month), 0) for month in all_months]

        chart = graph.Plot_Graph(x, y)

        context = {'chart': chart}
        return render(request, self.template_name, context)

class NoticeView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notice.html'
    context_object_name = 'notifications'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications = self.get_queryset()
                
        return context