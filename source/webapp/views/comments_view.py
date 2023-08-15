from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from webapp.forms import CommentForm
from webapp.models import Article, Comment, CommentLike


class CommentCreateView(CreateView):
    form_class = CommentForm
    template_name = "comments/comment_create.html"

    def form_valid(self, form):
        article = get_object_or_404(Article, pk=self.kwargs.get("pk"))
        comment = form.save(commit=False)
        comment.article = article
        comment.author = self.request.user
        comment.save()
        return redirect("webapp:article_view", pk=article.pk)


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/update_comment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["message"] = "test"
        return context

    def get_success_url(self):
        return reverse("webapp:article_view", kwargs={"pk": self.object.article.pk})


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        return reverse("webapp:article_view", kwargs={"pk": self.object.article.pk})

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class ToggleCommentLikeView(View):
    def post(self, request, pk: int):
        comment = get_object_or_404(Comment, pk=pk)
        user = request.user
        liked = CommentLike.objects.filter(comment=comment, user=user).exists()

        if liked:
            CommentLike.objects.filter(comment=comment, user=user).delete()
        else:
            CommentLike.objects.create(comment=comment, user=user)

        like_count = CommentLike.objects.filter(comment=comment).count()

        return JsonResponse({'count': like_count, 'liked': not liked})
