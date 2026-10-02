"""Tests for the news application."""

from datetime import timedelta

from django.contrib import admin
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article, Author, Category


class ModelTests(TestCase):
    """Verify the models, their relations and the computed URLs."""

    def setUp(self):
        self.author = Author.objects.create(name='Ana Torres')
        self.category = Category.objects.create(
            name='Tecnología',
            slug='tecnologia',
        )
        self.article = Article.objects.create(
            title='Sample Article',
            slug='sample-article',
            summary='A short summary used in the tests.',
            body='First paragraph.\n\nSecond paragraph.',
            author=self.author,
        )
        self.article.categories.set([self.category])

    def test_str_methods(self):
        self.assertEqual(str(self.author), 'Ana Torres')
        self.assertEqual(str(self.category), 'Tecnología')
        self.assertEqual(str(self.article), 'Sample Article')

    def test_article_relations(self):
        self.assertEqual(self.author.articles.count(), 1)
        self.assertEqual(self.category.articles.count(), 1)
        self.assertEqual(self.article.categories.count(), 1)

    def test_get_absolute_url_for_article(self):
        self.assertEqual(
            self.article.get_absolute_url(),
            reverse('news:article_detail', kwargs={'slug': 'sample-article'}),
        )

    def test_get_absolute_url_for_category(self):
        self.assertEqual(
            self.category.get_absolute_url(),
            reverse('news:category_list', kwargs={'slug': 'tecnologia'}),
        )

    def test_articles_are_ordered_by_published_at_descending(self):
        older = Article.objects.create(
            title='Older',
            slug='older',
            summary='Summary',
            body='Body',
            author=self.author,
            published_at=timezone.now() - timedelta(days=10),
        )
        newest = Article.objects.create(
            title='Newest',
            slug='newest',
            summary='Summary',
            body='Body',
            author=self.author,
            published_at=timezone.now(),
        )
        ordered = list(Article.objects.all())
        self.assertEqual(ordered, [newest, self.article, older])

    def test_author_is_protected_while_it_has_articles(self):
        with self.assertRaises(ProtectedError):
            self.author.delete()


class AdminConfigTests(TestCase):
    """Verify the ModelAdmin options of the news application."""

    def test_all_models_are_registered(self):
        registered = {
            model.__name__
            for model in admin.site._registry
            if model._meta.app_label == 'news'
        }
        self.assertEqual(registered, {'Article', 'Author', 'Category'})

    def test_article_admin_options(self):
        article_admin = admin.site._registry[Article]
        self.assertEqual(article_admin.date_hierarchy, 'published_at')
        self.assertEqual(
            set(article_admin.search_fields),
            {'title', 'summary', 'body'},
        )
        self.assertEqual(set(article_admin.filter_horizontal), {'categories'})
        self.assertEqual(
            set(article_admin.readonly_fields),
            {'created_at', 'updated_at'},
        )

    def test_category_admin_prepopulates_the_slug(self):
        category_admin = admin.site._registry[Category]
        self.assertEqual(
            category_admin.prepopulated_fields,
            {'slug': ('name',)},
        )


class HomeViewTests(TestCase):
    """Verify the front page of the portal."""

    def setUp(self):
        self.author = Author.objects.create(name='Luis Ramírez')
        self.category = Category.objects.create(name='Ciencia', slug='ciencia')
        self.published = Article.objects.create(
            title='Published',
            slug='published',
            summary='Visible article.',
            body='Body',
            author=self.author,
        )
        self.draft = Article.objects.create(
            title='Draft',
            slug='draft',
            summary='Hidden article.',
            body='Body',
            author=self.author,
            is_published=False,
        )

    def test_home_returns_200_and_uses_the_expected_templates(self):
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/home.html')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'partials/_article_card.html')

    def test_home_lists_only_published_articles(self):
        response = self.client.get(reverse('news:home'))
        titles = [article.title for article in response.context['articles']]
        self.assertEqual(titles, ['Published'])

    def test_home_exposes_the_categories_for_the_sidebar(self):
        response = self.client.get(reverse('news:home'))
        names = [category.name for category in response.context['categories']]
        self.assertEqual(names, ['Ciencia'])

    def test_home_shows_the_empty_state_without_articles(self):
        self.published.delete()
        response = self.client.get(reverse('news:home'))
        self.assertContains(response, 'No hay noticias publicadas todavía.')


class ArticleDetailViewTests(TestCase):
    """Verify the article detail page and the automatic escaping."""

    RAW_HTML = '<p>Este es un <strong>párrafo importante</strong> de prueba.</p>'

    def setUp(self):
        self.author = Author.objects.create(name='Sofía Delgado')
        self.category = Category.objects.create(name='Cultura', slug='cultura')
        self.article = Article.objects.create(
            title='Detail Article',
            slug='detail-article',
            summary='Summary',
            body=self.RAW_HTML,
            author=self.author,
        )
        self.article.categories.set([self.category])

    def test_detail_returns_200_with_the_article(self):
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': 'detail-article'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'news/article_detail.html')
        self.assertEqual(response.context['article'], self.article)

    def test_detail_returns_404_for_an_unpublished_article(self):
        self.article.is_published = False
        self.article.save()
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': 'detail-article'})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_escapes_the_raw_html_of_the_body(self):
        response = self.client.get(
            reverse('news:article_detail', kwargs={'slug': 'detail-article'})
        )
        escaped = (
            '&lt;p&gt;Este es un &lt;strong&gt;párrafo importante'
            '&lt;/strong&gt; de prueba.&lt;/p&gt;'
        )
        self.assertContains(response, escaped, html=False)
        self.assertNotContains(response, '<strong>párrafo importante</strong>')


class CategoryListViewTests(TestCase):
    """Verify the listing of articles by category."""

    def setUp(self):
        self.author = Author.objects.create(name='Ana Torres')
        self.category = Category.objects.create(
            name='Tecnología',
            slug='tecnologia',
            description='Noticias sobre tecnología.',
        )
        self.other = Category.objects.create(name='Ciencia', slug='ciencia')
        self.inside = Article.objects.create(
            title='Inside',
            slug='inside',
            summary='Summary',
            body='Body',
            author=self.author,
        )
        self.inside.categories.set([self.category])
        self.outside = Article.objects.create(
            title='Outside',
            slug='outside',
            summary='Summary',
            body='Body',
            author=self.author,
        )
        self.outside.categories.set([self.other])

    def test_category_list_returns_the_articles_of_the_category(self):
        response = self.client.get(
            reverse('news:category_list', kwargs={'slug': 'tecnologia'})
        )
        self.assertEqual(response.status_code, 200)
        titles = [article.title for article in response.context['articles']]
        self.assertEqual(titles, ['Inside'])

    def test_category_list_returns_404_for_an_unknown_slug(self):
        response = self.client.get(
            reverse('news:category_list', kwargs={'slug': 'unknown'})
        )
        self.assertEqual(response.status_code, 404)

    def test_category_list_excludes_unpublished_articles(self):
        self.inside.is_published = False
        self.inside.save()
        response = self.client.get(
            reverse('news:category_list', kwargs={'slug': 'tecnologia'})
        )
        self.assertContains(response, 'Esta categoría no tiene noticias.')


class UrlResolutionTests(TestCase):
    """Verify that the slug converter only matches valid slugs."""

    def test_article_slug_with_spaces_is_not_matched(self):
        response = self.client.get('/article/has space/')
        self.assertEqual(response.status_code, 404)
