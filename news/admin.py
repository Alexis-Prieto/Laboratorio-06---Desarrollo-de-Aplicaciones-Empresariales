"""Admin customisation for the news application.

The admin classes below replace the plain ``admin.site.register(Model)``
shortcut so that the columns, filters, search fields and slug helpers used by
the editorial team can be defined explicitly.
"""

from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administration options for the Author model."""

    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20
    ordering = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Administration options for the Category model."""

    list_display = ('name', 'slug', 'articles_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    ordering = ('name',)

    @admin.display(description='Articles')
    def articles_count(self, obj):
        """Return the number of articles that belong to the category."""
        return obj.articles.count()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Administration options for the Article model."""

    list_display = (
        'title',
        'author',
        'published_at',
        'is_published',
        'categories_count',
    )
    list_filter = ('is_published', 'categories', 'published_at')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('author',)
    list_per_page = 20

    @admin.display(description='# Categories')
    def categories_count(self, obj):
        """Return the number of categories linked to the article."""
        return obj.categories.count()
