from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import urlencode

from django.urls import reverse_lazy
from django.views import View

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from webapp.forms import ArticleForm, SearchForm
from webapp.models import Article, ArticleLike


class ArticleListView(ListView):
    model = Article
    template_name = "articles/index.html"
    context_object_name = "articles"
    ordering = ("-updated_at",)
    paginate_by = 3

    def dispatch(self, request, *args, **kwargs):
        print(request.path)

        self.form = self.get_search_form()
        self.search_value = self.get_search_value()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)
        context["form"] = self.form
        if self.search_value:
            context["query"] = urlencode({'search': self.search_value})
            context["search_value"] = self.search_value
        return context

    def get_search_form(self):
        return SearchForm(self.request.GET)

    def get_search_value(self):
        if self.form.is_valid():
            return self.form.cleaned_data['search']
        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        print(self.search_value)
        if self.search_value:
            queryset = queryset.filter(Q(title__icontains=self.search_value) |
                                       Q(author__icontains=self.search_value))
        return queryset


class ArticleCreateView(LoginRequiredMixin, CreateView):
    form_class = ArticleForm
    template_name = "articles/create_article.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArticleUpdateView(PermissionRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "articles/update_article.html"
    permission_required = "webapp.change_article"

    def has_permission(self):
        return super().has_permission() or self.get_object().author == self.request.user


class ArticleDeleteView(PermissionRequiredMixin, DeleteView):
    model = Article
    template_name = "articles/delete_article.html"
    success_url = reverse_lazy("webapp:index")

    def has_permission(self):
        return self.request.user.has_perm("webapp.delete_article") or \
            self.get_object().author == self.request.user


class ArticleDetailView(LoginRequiredMixin, DetailView):
    queryset = Article.objects.all()
    template_name = "articles/article.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.order_by("-updated_at")
        return context


class ToggleArticleLikeView(View):
    def post(self, request, pk: int):
        article = get_object_or_404(Article, pk=pk)
        user = request.user
        liked = ArticleLike.objects.filter(article=article, user=user).exists()

        if liked:
            ArticleLike.objects.filter(article=article, user=user).delete()
        else:
            ArticleLike.objects.create(article=article, user=user)

        like_count = ArticleLike.objects.filter(article=article).count()

        return JsonResponse({'count': like_count, 'liked': not liked})


