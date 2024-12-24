from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.views.generic.edit import FormView
from django.http import Http404

from .forms import PostForm, CommentForm, ProfileEditForm
from .models import Post, Category, Comment
from .utils import filter_posts


PER_PAGE = 10


class RegisterView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = PER_PAGE

    def get_queryset(self):
        profile = get_object_or_404(User,
                                    username=self.kwargs['username'])
        self.extra_context = {'profile': profile}
        return Post.objects.select_related(
            'location', 'author', 'category')\
            .filter(author=profile.pk)\
            .annotate(comment_count=Count("comments"))\
            .order_by('-pub_date')


class EditProfileView(LoginRequiredMixin, FormView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'page_obj'
    paginate_by = PER_PAGE

    def get_queryset(self):
        posts = Post.objects.select_related(
            'author', 'category', 'location')\
            .annotate(comment_count=Count('comments'))\
            .order_by('-pub_date')
        return filter_posts(posts)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dt_now = timezone.now()
        post = self.object

        if self.request.user != post.author:
            if not (post.pub_date <= dt_now
                    and post.is_published
                    and post.category.is_published):
                raise Http404

        context['form'] = CommentForm()
        context['comments'] = post.comments.\
            select_related('author')
        return context


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = PER_PAGE

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        self.extra_context = {'category': category}
        return filter_posts(category.posts.select_related(
            'author', 'category', 'location'
        ).order_by(('-pub_date')))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostEditView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        if (
            not self.request.user.is_authenticated
            or not self.test_func()
        ):
            return redirect(f'/posts/{self.kwargs["post_id"]}/')
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            'post_id': self.object.pk
        })


class PostDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        if (
            not self.request.user.is_authenticated
            or not self.test_func()
        ):
            return redirect(f'/posts/{self.kwargs["post_id"]}/')
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy("blog:profile", kwargs={
            'username': self.request.user.username
        })


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={
            "post_id": self.kwargs['post_id']
        })


@login_required
def comment_edit_view(request, post_id, comment_id):

    comment = get_object_or_404(
        Comment,
        pk=comment_id
    )

    if request.method == 'POST':

        comment_form = CommentForm(request.POST)
        if request.user.pk == comment.author.pk:

            if comment_form.is_valid():
                comment.text = comment_form.cleaned_data["text"]
                comment.save()

        return redirect('blog:post_detail', post_id=post_id)

    else:
        comment_form = CommentForm(instance=comment)
        context = {
            'form': comment_form,
            'comment': comment
        }

        return render(request, 'blog/comment.html', context)


@login_required
def comment_delete_view(request, post_id, comment_id):

    comment = get_object_or_404(
        Comment,
        pk=comment_id
    )
    if request.method == 'POST':

        if request.user.pk == comment.author.pk:
            comment.delete()

        return redirect('blog:post_detail', post_id=post_id)

    else:
        context = {
            'comment': comment
        }

        return render(request, 'blog/comment.html', context)
