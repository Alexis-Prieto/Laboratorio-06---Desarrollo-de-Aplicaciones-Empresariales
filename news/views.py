"""Public views for the news application.

Every view keeps the business logic (which records are visible, how they are
ordered and which related rows are needed) inside the view, so the templates
only receive plain querysets and display them.
"""

from django.shortcuts import get_object_or_404, render

from .models import Article, Category


def home(request):
    """Render the front page with the latest published articles."""
    articles = (
        Article.objects.filter(is_published=True)
        .select_related('author')
        .prefetch_related('categories')
    )
    categories = Category.objects.all()
    context = {
        'articles': articles,
        'categories': categories,
    }
    return render(request, 'news/home.html', context)


def article_detail(request, slug):
    """Render the full article identified by its slug."""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    context = {
        'article': article,
        'categories': Category.objects.all(),
    }
    return render(request, 'news/article_detail.html', context)


def category_list(request, slug):
    """Render all the published articles that belong to a category."""
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.filter(
        is_published=True,
    ).select_related('author')
    context = {
        'category': category,
        'articles': articles,
        'categories': Category.objects.all(),
    }
    return render(request, 'news/category_list.html', context)
