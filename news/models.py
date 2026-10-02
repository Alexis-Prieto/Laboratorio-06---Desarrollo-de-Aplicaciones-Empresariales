"""Database models for the news application."""

from django.db import models
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    """A journalist or contributor who writes articles."""

    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    photo = models.ImageField(
        upload_to='authors/',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.name


class Category(models.Model):
    """A thematic section used to group related articles."""

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return the public URL of the category listing page."""
        return reverse('news:category_list', kwargs={'slug': self.slug})


class Article(models.Model):
    """A news article published in the portal."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    summary = models.TextField(max_length=300)
    body = models.TextField()
    featured_image = models.ImageField(
        upload_to='articles/',
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name='articles',
    )
    categories = models.ManyToManyField(
        Category,
        related_name='articles',
        blank=True,
    )
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Return the public URL of the article detail page."""
        return reverse('news:article_detail', kwargs={'slug': self.slug})
