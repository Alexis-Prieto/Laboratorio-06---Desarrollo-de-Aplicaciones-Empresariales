# ENTREGABLE — Laboratorio N.° 6: Motor de plantillas con Django

**Curso:** Desarrollo de Aplicaciones Empresariales
**Institución:** TECSUP
**Docente:** Michael Montgomery Rosell
**Alumno:** Alexis Prieto Huiza
**Semana:** Semana 06
**Fecha:** 02/10/26

---

## Nota sobre la modalidad

> Este laboratorio fue desarrollado de forma **INDIVIDUAL** por **Alexis Prieto
> Huiza**. Todas las decisiones técnicas, la escritura del código, la ejecución
> de los comandos, las pruebas y las capturas corresponden a un único
> estudiante.

---

## Índice

1. [Entorno de desarrollo](#entorno-de-desarrollo)
2. [Paso 1 — Setup inicial](#paso-1--setup-inicial)
3. [Paso 2 — Configuración de `settings.py` y `config/urls.py`](#paso-2--configuración-de-settingspy-y-configurlspy)
4. [Paso 3 — Modelos, migraciones y superusuario](#paso-3--modelos-migraciones-y-superusuario)
5. [Paso 4 — Plantilla base con herencia](#paso-4--plantilla-base-con-herencia)
6. [Paso 5 — Fragmento reutilizable `_article_card.html`](#paso-5--fragmento-reutilizable-_article_cardhtml)
7. [Paso 6 — Plantilla de portada](#paso-6--plantilla-de-portada)
8. [Paso 7 — Plantilla de detalle](#paso-7--plantilla-de-detalle)
9. [Paso 8 — Plantilla de listado por categoría](#paso-8--plantilla-de-listado-por-categoría)
10. [Paso 9 — Rutas y vistas](#paso-9--rutas-y-vistas)
11. [Paso 10 — Estilos](#paso-10--estilos)
12. [Paso 11 — Admin personalizado y datos de prueba](#paso-11--admin-personalizado-y-datos-de-prueba)
13. [Paso 12 — Escapado automático](#paso-12--escapado-automático)
14. [Paso 13 — Entregable y Git](#paso-13--entregable-y-git)
15. [Decisiones de diseño](#decisiones-de-diseño)
16. [Supuestos](#supuestos)
17. [Pruebas automatizadas](#pruebas-automatizadas)
18. [Conclusiones](#conclusiones)
19. [Anexo — Capturas del sistema en funcionamiento](#anexo--capturas-del-sistema-en-funcionamiento)

---

## Entorno de desarrollo

| Componente | Versión |
| --- | --- |
| Python | 3.13.5 |
| Django | 5.0.6 |
| Pillow | 10.4.0 |
| python-dotenv | 1.0.1 |
| Base de datos | SQLite 3 |
| Sistema operativo | Windows 11 (PowerShell) |
| Navegador de pruebas | Microsoft Edge |

Comprobación del entorno antes de empezar:

```powershell
py -3.13 -m venv venv
.\venv\Scripts\python.exe -c "import sys, PIL, django; print(sys.version.split()[0], PIL.__version__, django.get_version())"
# 3.13.5 10.4.0 5.0.6
```

---

## Paso 1 — Setup inicial

El proyecto es la **continuación del Laboratorio N.° 5**: se reutiliza el
proyecto `config` con la aplicación `movies` y se **agrega** la aplicación
`news`. No se modificó ningún archivo de la aplicación existente salvo
`settings.py` y `config/urls.py`, que son puntos de configuración compartidos.

### Comandos ejecutados

```powershell
# a) Verificar Pillow (Paso 1a)
.\venv\Scripts\python.exe -c "import PIL; print(PIL.__version__)"
# 10.4.0

# b) Crear la aplicación (Paso 1b)
python manage.py startapp news
```

### Verificación de la estructura creada

```text
news/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

### Código: `news/apps.py`

```python
"""Application configuration for the news app."""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    """Configuration class for the news application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
```

**Resultado.** `startapp` generó el esqueleto estándar de la aplicación y
`apps.py` quedó con la clase `NewsConfig` que Django descubre automáticamente
al registrar la app en `INSTALLED_APPS`.

### Tabla de casos de prueba — Paso 1

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 1.1 | `import PIL` | Versión 10.4.0 | 10.4.0 | ✔ |
| 1.2 | `manage.py startapp news` | Crear el paquete `news` | Paquete creado | ✔ |
| 1.3 | `import django` | Versión 5.0.6 | 5.0.6 | ✔ |

---

## Paso 2 — Configuración de `settings.py` y `config/urls.py`

### Código: `config/settings.py` (fragmentos agregados)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'movies',
    'news',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

> La clave secreta y el modo depuración siguen leyéndose desde `.env` con
> `python-dotenv` (trabajo del Laboratorio N.° 5). **No** se escribió ninguna
> credencial en el código.

### Código: `config/urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
    path('', include('movies.urls')),
]

# Serve the uploaded media files (posters and article images) in development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Resultado.** `DIRS` apunta a la carpeta global `templates/`, mientras que
`APP_DIRS = True` mantiene la plantilla `movies/templates/movies/…` funcionando
sin cambios. La aplicación `news` se incluye **antes** que `movies` para que su
vista `home` atienda la raíz `/`; los patrones son disjuntos, por lo que la
vista `recommendations` del Laboratorio N.° 5 sigue resolviendo igual.

### Tabla de casos de prueba — Paso 2

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 2.1 | `manage.py check` | 0 issues | `System check identified no issues (0 silenced).` | ✔ |
| 2.2 | Ver `/{raíz}` | Portada del portal | HTTP 200 con la portada | ✔ |
| 2.3 | Ver `/recommendations/1/` | Vista del Lab 05 intacta | HTTP 200 | ✔ |
| 2.4 | Cargar la hoja de estilos | `{% static %}` resuelto | `/static/news/css/style.css` presente | ✔ |

---

## Paso 3 — Modelos, migraciones y superusuario

### Código: `news/models.py`

```python
"""Database models for the news application."""

from django.db import models
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    """A journalist or contributor who writes articles."""

    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='authors/', null=True, blank=True)

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
        upload_to='articles/', null=True, blank=True,
    )
    author = models.ForeignKey(
        Author, on_delete=models.PROTECT, related_name='articles',
    )
    categories = models.ManyToManyField(
        Category, related_name='articles', blank=True,
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
```

> En el archivo final los argumentos de `ImageField`, `ForeignKey` y
> `ManyToManyField` se escriben uno por línea para respetar PEP 8 (79 columnas).
> Aquí se compactan para que el bloque sea legible.

### Comandos ejecutados

```powershell
python manage.py makemigrations news
python manage.py migrate
```

### Salida

```text
Migrations for 'news':
  news\migrations\0001_initial.py
    - Create model Author
    - Create model Category
    - Create model Article

  Applying movies.0001_initial... OK
  Applying news.0001_initial... OK
  Applying sessions.0001_initial... OK
```

### Verificación del superusuario

```powershell
python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())"
# SUPERUSER_EXISTS False

$env:DJANGO_SUPERUSER_USERNAME="admin"
$env:DJANGO_SUPERUSER_EMAIL="admin@example.com"
$env:DJANGO_SUPERUSER_PASSWORD="Admin12345!"
python manage.py createsuperuser --noinput
# Superuser created successfully.
```

> La contraseña se pasó por **variable de entorno** en la línea de comandos y
> la sesión se limpió con `Remove-Item Env:...`; nunca se guardó en el
> repositorio.

**Resultado.** La migración `news/0001_initial.py` crea las tres tablas con sus
relaciones. `on_delete=PROTECT` en `Article.author` impide borrar un autor que
todavía tenga artículos, comportamiento comprobado con una prueba automatizada.

### Tabla de casos de prueba — Paso 3

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 3.1 | `makemigrations news` | Crear `0001_initial` | `news\migrations\0001_initial.py` | ✔ |
| 3.2 | `migrate` | Aplicar sin errores | `Applying news.0001_initial... OK` | ✔ |
| 3.3 | Verificar superusuario | Debe existir | No existía → creado `admin` | ✔ |
| 3.4 | Borrar un `Author` con artículos | `ProtectedError` | `ProtectedError` | ✔ |

---

## Paso 4 — Plantilla base con herencia

### Código: `templates/base.html`

```html
{% load static %}<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Noticias{% endblock %}</title>
  <meta name="description" content="Portal de noticias de Tecnología, Ciencia y Cultura.">
  <link rel="stylesheet" href="{% static 'news/css/style.css' %}">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{% url 'news:home' %}">
        <span class="brand-mark">PN</span>
        <span class="brand-name">Portal de Noticias</span>
      </a>
      <nav class="main-nav" aria-label="Categorías">
        {% for cat in categories %}
          <a href="{% url 'news:category_list' cat.slug %}">{{ cat.name }}</a>
        {% endfor %}
      </nav>
    </div>
  </header>

  <div class="container layout">
    <main class="content">
      {% block content %}{% endblock %}
    </main>

    <aside class="sidebar">
      {% block sidebar %}
        <h2 class="sidebar-title">Categorías</h2>
        <ul class="category-list">
          {% for cat in categories %}
            <li>
              <a href="{% url 'news:category_list' cat.slug %}">
                {{ cat.name }}
              </a>
            </li>
          {% empty %}
            <li class="muted">Sin categorías registradas.</li>
          {% endfor %}
        </ul>
      {% endblock %}
    </aside>
  </div>

  <footer class="site-footer">
    <div class="container">
      <p>
        &copy; {% now "Y" %} Portal de Noticias — Tecsup.
        Todos los derechos reservados.
      </p>
    </div>
  </footer>
</body>
</html>
```

**Resultado.** La plantilla define tres bloques (`title`, `content` y
`sidebar`) y resuelve la hoja de estilos con `{% static %}`. El pie de página
usa el tag `{% now "Y" %}` para no escribir el año a mano.

### Tabla de casos de prueba — Paso 4

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 4.1 | Cargar `/` | Header, contenido, sidebar y footer | Los cuatro bloques presentes | ✔ |
| 4.2 | Ver el título de la pestaña | `Portada — Portal de Noticias` | Correcto (`{% block title %}` sobreescrito) | ✔ |
| 4.3 | Pedir `/static/news/css/style.css` | Respuesta 200 | 200 (servida por `staticfiles`) | ✔ |

---

## Paso 5 — Fragmento reutilizable `_article_card.html`

### Código: `templates/partials/_article_card.html`

```html
{% comment %}
Reusable article card. It expects an `article` object in the context and does
not include <html>, <head> or <body>, so it can be included from any template.
{% endcomment %}
<article class="card">
  {% if article.featured_image %}
    <img class="card-image" src="{{ article.featured_image.url }}" alt="{{ article.title }}">
  {% else %}
    <div class="card-image card-image--placeholder">
      <span>{{ article.title|truncatechars:45 }}</span>
    </div>
  {% endif %}

  <div class="card-body">
    <p class="card-meta">
      <span class="card-date">{{ article.published_at|date:"d M Y" }}</span>
      <span class="card-author">{{ article.author.name }}</span>
    </p>

    <h2 class="card-title">
      <a href="{% url 'news:article_detail' article.slug %}">{{ article.title }}</a>
    </h2>

    <p class="card-summary">{{ article.summary|truncatewords:20 }}</p>

    {% if article.categories.all %}
      <ul class="card-tags">
        {% for cat in article.categories.all %}
          <li>
            <a href="{% url 'news:category_list' cat.slug %}">{{ cat.name }}</a>
          </li>
        {% endfor %}
      </ul>
    {% endif %}
  </div>
</article>
```

**Resultado.** El fragmento **no** contiene `<html>`, `<head>` ni `<body>`, por
lo que puede incluirse tantas veces como se quiera dentro de cualquier
plantilla que extienda `base.html`. Usa los filtros `|truncatewords:20`,
`|truncatechars:45` y `|date:"d M Y"`, y resuelve los enlaces con `{% url %}`.

### Tabla de casos de prueba — Paso 5

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 5.1 | Incluir el fragmento en `/` | 6 tarjetas | 6 tarjetas (`class="card"`) | ✔ |
| 5.2 | Artículo sin imagen | Bloque de respaldo con degradado | Se muestra el placeholder | ✔ |
| 5.3 | Resumen largo | Cortado a 20 palabras | `|truncatewords:20` aplicado | ✔ |
| 5.4 | Enlace de la tarjeta | `{% url %}` resuelto | `/article/<slug>/` | ✔ |

---

## Paso 6 — Plantilla de portada

### Código: `templates/news/home.html`

```html
{% extends 'base.html' %}

{% block title %}Portada — Portal de Noticias{% endblock %}

{% block content %}
  <h1 class="page-title">Últimas noticias</h1>

  <div class="grid">
    {% for article in articles %}
      {% include 'partials/_article_card.html' %}
    {% empty %}
      <p class="empty-state">No hay noticias publicadas todavía.</p>
    {% endfor %}
  </div>
{% endblock %}

{% block sidebar %}
  <h2 class="sidebar-title">Categorías</h2>
  <ul class="category-list">
    {% for cat in categories %}
      <li>
        <a href="{% url 'news:category_list' cat.slug %}">
          {{ cat.name }}
          <span class="count">{{ cat.articles.count }}</span>
        </a>
      </li>
    {% empty %}
      <li class="muted">Sin categorías registradas.</li>
    {% endfor %}
  </ul>
{% endblock %}
```

**Resultado.** La portada extiende `base.html`, recorre el queryset `articles`
incluyendo el mismo fragmento del Paso 5 y usa la rama `{% empty %}` para el
estado sin noticias. La barra lateral se sobreescribe con `{% block sidebar %}`.

### Tabla de casos de prueba — Paso 6

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 6.1 | Abrir `/` | 6 noticias en rejilla | 6 tarjetas | ✔ |
| 6.2 | `h1` de la portada | `Últimas noticias` | `Últimas noticias` | ✔ |
| 6.3 | Sidebar | 3 categorías con contador | 3 enlaces con `2` cada uno | ✔ |
| 6.4 | Sin artículos publicados | «No hay noticias publicadas todavía.» | Mensaje mostrado | ✔ |

---

## Paso 7 — Plantilla de detalle

### Código: `templates/news/article_detail.html`

```html
{% extends 'base.html' %}

{% block title %}{{ article.title }}{% endblock %}

{% block content %}
  <article class="article">
    <h1 class="article-title">{{ article.title }}</h1>

    <p class="article-meta">
      Por {{ article.author.name }} —
      {{ article.published_at|date:"d \d\e F \d\e Y" }}
    </p>

    {% if article.featured_image %}
      <img class="article-image" src="{{ article.featured_image.url }}" alt="{{ article.title }}">
    {% endif %}

    <p class="article-summary">{{ article.summary }}</p>

    <div class="article-body">
      {{ article.body|linebreaks }}
    </div>

    <footer class="article-footer">
      <span class="label">Categorías:</span>
      {% for cat in article.categories.all %}
        <a class="badge" href="{% url 'news:category_list' cat.slug %}">
          {{ cat.name }}
        </a>
      {% empty %}
        <span class="muted">Sin categoría</span>
      {% endfor %}
    </footer>

    <p class="article-back">
      <a href="{% url 'news:home' %}">&larr; Volver a la portada</a>
    </p>
  </article>
{% endblock %}
```

**Resultado.** El título de la pestaña es el del artículo y el cuerpo se
renderiza con `|linebreaks`, que convierte cada salto de línea en un párrafo
`<p>` real. La fecha se formatea como «23 de septiembre de 2026» gracias a
`LANGUAGE_CODE = 'es'`.

### Tabla de casos de prueba — Paso 7

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 7.1 | Abrir `/article/<slug>/` | Detalle completo | HTTP 200 | ✔ |
| 7.2 | Párrafos del cuerpo | Convertidos a `<p>` | `|linebreaks` aplicado | ✔ |
| 7.3 | Fecha | `d de F de Y` en español | `23 de septiembre de 2026` | ✔ |
| 7.4 | Slug inexistente | HTTP 404 | HTTP 404 | ✔ |
| 7.5 | Artículo `is_published=False` | HTTP 404 | HTTP 404 | ✔ |

---

## Paso 8 — Plantilla de listado por categoría

### Código: `templates/news/category_list.html`

```html
{% extends 'base.html' %}

{% block title %}{{ category.name }} — Portal de Noticias{% endblock %}

{% block content %}
  <h1 class="page-title">Categoría: {{ category.name }}</h1>

  {% if category.description %}
    <p class="page-description">{{ category.description }}</p>
  {% endif %}

  <div class="grid">
    {% for article in articles %}
      {% include 'partials/_article_card.html' %}
    {% empty %}
      <p class="empty-state">Esta categoría no tiene noticias.</p>
    {% endfor %}
  </div>
{% endblock %}
```

**Resultado.** El **mismo fragmento** del Paso 5 se reutiliza aquí sin
duplicar una sola línea de HTML, lo que demuestra la reutilización exigida por
la rúbrica (C1). La descripción de la categoría solo se imprime si existe
(`{% if %}`).

### Tabla de casos de prueba — Paso 8

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 8.1 | Abrir `/category/tecnologia/` | 2 noticias de la categoría | 2 tarjetas | ✔ |
| 8.2 | Categoría sin noticias publicadas | «Esta categoría no tiene noticias.» | Mensaje mostrado | ✔ |
| 8.3 | Slug inexistente | HTTP 404 | HTTP 404 | ✔ |

---

## Paso 9 — Rutas y vistas

### Código: `news/views.py`

```python
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
```

### Código: `news/urls.py`

```python
"""URL patterns for the news application."""

from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'article/<slug:slug>/',
        views.article_detail,
        name='article_detail',
    ),
    path(
        'category/<slug:slug>/',
        views.category_list,
        name='category_list',
    ),
]
```

### Verificación: no hay URLs escritas a mano en las plantillas

```powershell
# Búsqueda de enlaces absolutos en templates/
Select-String -Path templates\*\*.html, templates\*.html -Pattern 'href="/' -SimpleMatch
# (sin resultados)
```

Todas las rutas se generan con `{% url 'news:…' %}`:

| Plantilla | Tag usado |
| --- | --- |
| `base.html` | `{% url 'news:home' %}`, `{% url 'news:category_list' cat.slug %}` |
| `_article_card.html` | `{% url 'news:article_detail' article.slug %}`, `{% url 'news:category_list' cat.slug %}` |
| `home.html` | `{% url 'news:category_list' cat.slug %}` |
| `article_detail.html` | `{% url 'news:category_list' cat.slug %}`, `{% url 'news:home' %}` |

**Resultado.** Las tres vistas devuelven HTTP 200 con el contexto esperado y
los `get_object_or_404` protegen los artículos no publicados (404 en lugar de
mostrarlos). La lógica de filtrado (`is_published`) y de orden vive en las
vistas, nunca en las plantillas.

### Tabla de casos de prueba — Paso 9

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 9.1 | `reverse('news:home')` | `/` | `/` | ✔ |
| 9.2 | `reverse('news:article_detail', slug=…)` | `/article/<slug>/` | Correcto | ✔ |
| 9.3 | `reverse('news:category_list', slug=…)` | `/category/<slug>/` | Correcto | ✔ |
| 9.4 | Buscar `href="/"` en `templates/` | Sin coincidencias | Sin coincidencias | ✔ |
| 9.5 | `/article/<slug con espacios>/` | HTTP 404 (conversor `slug`) | HTTP 404 | ✔ |

---

## Paso 10 — Estilos

### Código: `static/news/css/style.css` (fragmentos)

```css
/* Portal de Noticias - Lab 06
   Colour palette: background #f8fafc, primary #4f46e5, text #1f2937. */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

:root {
  --bg: #f8fafc;
  --primary: #4f46e5;
  --primary-light: #6366f1;
  --text: #1f2937;
  --muted: #6b7280;
  --surface: #ffffff;
  --border: #e5e7eb;
  --shadow-sm: 0 4px 6px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 20px 25px rgba(0, 0, 0, 0.15);
  --radius: 16px;
}

body {
  font-family: 'Inter', 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.site-header {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #ffffff;
  box-shadow: 0 10px 30px rgba(79, 70, 229, 0.3);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.card {
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
```

El archivo completo incluye además los estilos de la barra lateral
(`.category-list`), del detalle del artículo (`.article`, `.article-body`,
`.badge`) y del pie de página.

### Verificación de la carga del archivo

```html
<!-- templates/base.html -->
<link rel="stylesheet" href="{% static 'news/css/style.css' %}">
```

**Resultado.** La hoja de estilos se sirve desde `STATICFILES_DIRS`
(`static/news/css/style.css`) y `{% static %}` genera la URL `/static/news/css/style.css`.
La rejilla es responsive con `auto-fill`/`minmax(300px, 1fr)` y las tarjetas
se elevan al pasar el cursor.

### Tabla de casos de prueba — Paso 10

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 10.1 | Buscar `style.css` en el HTML | Etiqueta `<link>` presente | Presente | ✔ |
| 10.2 | Pedir `/static/news/css/style.css` | HTTP 200 | HTTP 200 | ✔ |
| 10.3 | Reducir la ventana a < 900 px | Sidebar bajo el contenido | Rejilla de 1 columna | ✔ |
| 10.4 | Pasar el cursor sobre una tarjeta | Elevación y sombra | `translateY(-8px)` | ✔ |

---

## Paso 11 — Admin personalizado y datos de prueba

### Código: `news/admin.py`

```python
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
```

### Comando de datos de prueba: `news/management/commands/seed_news.py`

El comando está decorado con `@transaction.atomic` y usa `get_or_create` para
ser **idempotente**. Genera:

* 3 categorías: Tecnología, Ciencia y Cultura (slug con `slugify`).
* 3 autores: Ana Torres, Luis Ramírez y Sofía Delgado.
* 6 artículos, repartidos 2 por categoría, con fechas de los últimos 30 días.

```python
        now = timezone.now()
        for data in ARTICLES:
            article, created = Article.objects.get_or_create(
                slug=slugify(data['title']),
                defaults={
                    'title': data['title'],
                    'summary': data['summary'],
                    'body': data['body'],
                    'author': authors[data['author']],
                    'published_at': now - timedelta(days=data['days_ago']),
                    'is_published': True,
                },
            )
            article.categories.set(
                categories[name] for name in data['categories']
            )
```

Uno de los artículos («Cinco hábitos para proteger tus datos personales»)
guarda **HTML crudo** en el cuerpo para poder demostrar el escapado automático
del Paso 12:

```python
        'body': (
            '<p>Este es un <strong>párrafo importante</strong> de prueba.</p>'
            '<p>El contenido de este artículo se guardó con etiquetas HTML '
            'reales para demostrar el escapado automático de Django.</p>'
        ),
```

### Ejecución

```powershell
python manage.py seed_news
```

```text
Created category: Tecnología
Created category: Ciencia
Created category: Cultura
Created author: Ana Torres
Created author: Luis Ramírez
Created author: Sofía Delgado
Created article: Inteligencia artificial en las aulas peruanas
Created article: Cinco hábitos para proteger tus datos personales
  -> cinco-habitos-para-proteger-tus-datos-personales stores raw HTML to
     demonstrate the automatic escaping (step 12).
Created article: Nuevo estudio sobre el agua en Marte
Created article: Cómo el sueño reordena la memoria
Created article: El festival de cine independiente vuelve a las salas
Created article: La novela gráfica peruana gana terreno
Seed finished: 3 categories, 3 authors, 6 articles.
```

### Segunda ejecución (prueba de idempotencia)

```text
Found category: Tecnología
Found category: Ciencia
Found category: Cultura
Found author: Ana Torres
…
Seed finished: 3 categories, 3 authors, 6 articles.
```

**Resultado.** El portal muestra 6 noticias sin tocar una sola línea de código:
todo el contenido se gestiona desde `/admin/`. La segunda ejecución del comando
informa `Found` y deja los conteos iguales (3/3/6), confirmando la idempotencia.

### Tabla de casos de prueba — Paso 11

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 11.1 | `manage.py seed_news` | 3 categorías, 3 autores, 6 artículos | Exactamente eso | ✔ |
| 11.2 | Ejecutar `seed_news` dos veces | No duplicar registros | `Found…` 3/3/6 | ✔ |
| 11.3 | `/admin/news/category/` | Columnas `name`, `slug`, `Articles` | Se muestran las 3 columnas | ✔ |
| 11.4 | `/admin/news/article/` | Filtros, búsqueda y jerarquía por fecha | `is_published`, `categories`, `published_at` | ✔ |
| 11.5 | Editar y publicar desde el admin | Aparece en el portal | Aparece sin tocar código | ✔ |
| 11.6 | Buscar `mesa` en artículos | Coincidencia en título/resumen/cuerpo | Encontrado | ✔ |

---

## Paso 12 — Escapado automático

### 1. Artículo con HTML crudo

El artículo con slug `cinco-habitos-para-proteger-tus-datos-personales` tiene
guardado en el campo `body`:

```html
<p>Este es un <strong>párrafo importante</strong> de prueba.</p>
<p>El contenido de este artículo se guardó con etiquetas HTML reales para
demostrar el escapado automático de Django.</p>
```

### 2. Plantilla usada

```html
<div class="article-body">
  {{ article.body|linebreaks }}
</div>
```

### 3. Qué se observa en el navegador

Al abrir `http://127.0.0.1:8000/article/cinco-habitos-para-proteger-tus-datos-personales/`
el navegador muestra las **etiquetas literales**:

```text
<p>Este es un <strong>párrafo importante</strong> de prueba.</p>
<p>El contenido de este artículo se guardó con etiquetas HTML reales para
demostrar el escapado automático de Django.</p>
```

El HTML realmente entregado por el servidor (verificado con el cliente de
pruebas de Django) es:

```html
<div class="article-body">
  <p>&lt;p&gt;Este es un &lt;strong&gt;párrafo importante&lt;/strong&gt; de prueba.&lt;/p&gt;&lt;p&gt;El contenido de este artículo…&lt;/p&gt;</p>
</div>
```

Es decir, los `<` y `>` se entregaron como `&lt;` y `&gt;`, por lo que el
navegador los dibuja como texto en lugar de interpretarlos como marcado.

### 4. Documentación

> Django aplica **escapado automático** a todas las variables en las plantillas
> para prevenir ataques XSS. Por eso, el HTML crudo guardado en el campo `body`
> se muestra como texto plano y **NO** se interpreta. Para mostrar HTML
> confiable habría que usar el filtro `|safe`, pero eso solo es seguro si el
> contenido proviene de una fuente controlada.

### 5. Comparación opcional con `{% autoescape off %}`

Se renderizó el **mismo** contenido con y sin escapado:

```django
{# Escapado activado (comportamiento por defecto) #}
{{ article.body }}

{# Escapado desactivado (solo para contenido confiable) #}
{% autoescape off %}{{ article.body }}{% endautoescape %}
```

Resultado de la comparación:

```text
autoescape ON : &lt;p&gt;Este es un &lt;strong&gt;párrafo importante&lt;/strong&gt; de prueba.&lt;/p&gt;
autoescape OFF: <p>Este es un <strong>párrafo importante</strong> de prueba.</p>
```

**Diferencia.** Con `autoescape off` el navegador **sí** interpreta las etiquetas
y aplica la negrita; el texto «párrafo importante» aparece en negrita y los
`<p>` no se ven. Es exactamente el comportamiento que Django evita por defecto,
porque permitir HTML sin sanear es la vía habitual de los ataques XSS. Por eso
el proyecto se queda con el comportamiento por defecto y **no** usa `|safe`.

### Tabla de casos de prueba — Paso 12

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 12.1 | Ver el detalle del artículo con HTML | Etiquetas como texto | `<p>` visible como texto | ✔ |
| 12.2 | Buscar `<strong>` en el HTML servido | No debe aparecer | No aparece | ✔ |
| 12.3 | Buscar `&lt;strong&gt;` en el HTML servido | Debe aparecer | Aparece | ✔ |
| 12.4 | `{% autoescape off %}` | El HTML sí se interpreta | Negrita renderizada | ✔ |

---

## Paso 13 — Entregable y Git

### Comandos ejecutados

```powershell
git add .
git commit -m "feat: lab06 motor de plantillas Django"
git branch -M main
```

### Estado del repositorio

```text
## main
```

> **No** se ejecutó `git push`: el envío al repositorio remoto queda a cargo
> del estudiante.

### Verificación final antes del commit

```powershell
python manage.py check            # System check identified no issues (0 silenced).
python manage.py test news movies # Ran 34 tests ... OK
```

```text
Ran 34 tests in 1.149s

OK
Destroying test database for alias 'default'...
```

**Resultado.** Se ejecutan las **34** pruebas del proyecto (las 20 nuevas de
`news` más las 14 heredadas de `movies`) sin fallos, lo que confirma que el
Laboratorio N.° 5 sigue funcionando intacto.

### Tabla de casos de prueba — Paso 13

| # | Acción | Esperado | Obtenido | OK |
| --- | --- | --- | --- | --- |
| 13.1 | `manage.py check` | 0 issues | 0 issues | ✔ |
| 13.2 | `manage.py test news movies` | 34 pruebas correctas | `Ran 34 tests … OK` | ✔ |
| 13.3 | `git commit` | Commit creado | Commit en la rama `main` | ✔ |
| 13.4 | `git branch -M main` | Rama renombrada | Rama activa `main` | ✔ |
| 13.5 | `git push` | No ejecutado | No ejecutado (a cargo del alumno) | ✔ |

---

## Decisiones de diseño

**1. `base.html` + `partials/_article_card.html` en lugar de plantillas
independientes.**
`base.html` concentra el `<head>`, el header, la rejilla de contenido y el
footer; cada página solo aporta lo que le es propio. La tarjeta de noticia se
extrae a un fragmento porque se dibuja de forma idéntica en la portada y en el
listado por categoría: al incluirla con `{% include %}` se escribe el HTML **una
sola vez** y un cambio de diseño se propaga a todas las vistas a la vez.

**2. Uso de `{% url %}` en lugar de rutas escritas a mano.**
Escribir `href="/article/mi-slug/"` obliga a tocar todas las plantillas si cambia
una ruta. Con `{% url 'news:article_detail' article.slug %}` cada URL se genera a
partir del nombre de la ruta y de sus argumentos, de modo que un cambio en
`news/urls.py` se refleja automáticamente y las plantillas nunca quedan rotas.

**3. `{% load static %}` para la hoja de estilos.**
`STATIC_URL` puede cambiar entre desarrollo y producción. Al referenciar el CSS
con `{% static 'news/css/style.css' %}` la etiqueta `<link>` apunta siempre al
prefijo correcto, sin escribir `/static/` a mano.

**4. Se mantiene el escapado automático (no se usa `|safe`).**
El Paso 12 demuestra que Django convierte `<` y `>` en `&lt;` y `&gt;`. Esa es la
protección por defecto contra XSS: si un redactor publicara contenido con
`<script>`, se mostraría como texto y no se ejecutaría. Desactivarlo con `|safe`
solo sería aceptable con contenido saneado en el servidor.

**5. `LANGUAGE_CODE = 'es'` para el filtro `|date` en español.**
El formato pedido (`d \d\e F \d\e Y`) imprime el nombre del mes según el idioma
activo. Con `en-us` el resultado sería «23 de September de 2026»; con `es` es
«23 de septiembre de 2026», coherente con un portal en español.

**6. `select_related('author')` y `prefetch_related('categories')` en las vistas.**
La portada y el listado por categoría recorren N artículos y, por cada uno,
acceden a su autor y a sus categorías. Cargar esas relaciones por adelantado
evita el problema de las *N+1 queries* sin cambiar el HTML ni la plantilla.

**7. Las categorías también llegan al detalle y al listado por categoría.**
El header y la barra lateral de `base.html` necesitan la lista `categories` para
ser iguales en todas las páginas. Como la lógica debe vivir en la vista y no en
la plantilla, se añade `'categories': Category.objects.all()` a los tres
contextos en lugar de incluir consultas dentro del HTML.

**8. La lógica de publicación (`is_published`) vive en las vistas.**
Tanto `home` como `category_list` filtran en la consulta y `article_detail` usa
`get_object_or_404(..., is_published=True)`. La plantilla recibe siempre datos
ya depurados y nunca decide qué es visible.

---

## Supuestos

1. **Proyecto de partida.** Se asume que el workspace ya contiene el proyecto del
   Laboratorio N.° 5 (`config` + aplicación `movies`). Esta entrega **agrega** la
   aplicación `news` y no reescribe nada de `movies`.

2. **Entorno virtual.** Como la instalación global de Python del equipo no tenía
   Django ni Pillow, se creó el entorno `venv` con `py -3.13 -m venv venv` y se
   instaló `requirements.txt` del propio repositorio. Todas las versiones
   coinciden con las exigidas (Python 3.13.5, Django 5.0.6, Pillow 10.4.0).

3. **Orden de inclusión de las URLs.** `news.urls` se incluye antes que
   `movies.urls` porque su vista `home` debe atender la raíz `/`. Los patrones de
   ambas aplicaciones son disjuntos (`''`, `article/…`, `category/…` frente a
   `recommendations/…`), por lo que esto **no** afecta al Laboratorio N.° 5: la
   prueba `GET /recommendations/1/` devuelve HTTP 200.

4. **`LANGUAGE_CODE`.** Se cambió de `en-us` a `es` para que el filtro `|date`
   imprima el mes en español, tal como pide el enunciado. `TIME_ZONE` se dejó en
   `UTC` igual que en el Laboratorio N.° 5 para no alterar el comportamiento
   existente.

5. **`.gitignore`.** El patrón `static/*` del Laboratorio N.° 5 excluía toda la
   carpeta `static/`, incluida la nueva hoja de estilos. Se añadieron excepciones
   para `static/news/css/style.css` y para `media/articles/.gitkeep` con el fin
   de que el repositorio entregado incluya los archivos exigidos. Fue la única
   modificación al archivo y resultó imprescindible para el criterio C4.

6. **`media/articles/.gitkeep`.** La carpeta de subida `media/articles/` se creó
   con un archivo `.gitkeep` (igual que hace `media/` en el Laboratorio N.° 5)
   porque esas dos carpetas ignoradas se crean solas en tiempo de ejecución y Git
   no versiona directorios vacíos.

7. **Slugs generados con `slugify`.** En `seed_news` el slug se deriva del título
   con `django.utils.text.slugify`, de modo que los títulos con tildes
   («Cómo el sueño reordena la memoria») producen slugs limpios y reproducibles
   (`como-el-sueno-reordena-la-memoria`).

8. **`summary` limitado a 300 caracteres.** El enunciado define
   `TextField(max_length=300)`. Ese límite se aplica en los formularios y en el
   admin de Django, no a nivel de SQLite; todos los resúmenes de `seed_news` son
   más cortos que el límite.

9. **Alcance de las pruebas.** Las tablas de casos de prueba se construyeron con
   el cliente de pruebas de Django (`django.test.Client`) y con la comprobación
   de las páginas desde el navegador. Los resultados «Obtenido» son salidas
   reales de esos comandos, no suposiciones.

10. **Rúbrica cubierta.** C1 (herencia y fragmento reutilizado), C2 (variables,
    tags y filtros), C3 (contenido gestionado desde el admin) y C4 (repositorio
    ordenado con este entregable).

---

## Pruebas automatizadas

El archivo `news/tests.py` contiene **20 pruebas** agrupadas en seis clases. Se
ejecutan junto con las 14 pruebas heredadas del Laboratorio N.° 5:

```powershell
python manage.py test news movies
```

```text
Ran 34 tests in 1.149s

OK
Destroying test database for alias 'default'...
```

| Clase | Qué verifica |
| --- | --- |
| `ModelTests` | `__str__`, relaciones M2M/FK, `get_absolute_url()`, orden por `-published_at` y `ProtectedError` al borrar un autor con artículos. |
| `AdminConfigTests` | Que las tres entidades estén registradas y que las opciones de `ModelAdmin` (búsqueda, filtros, `filter_horizontal`, campos de solo lectura, `prepopulated_fields`) sean las esperadas. |
| `HomeViewTests` | HTTP 200, plantillas usadas (`home.html`, `base.html` y `partials/_article_card.html`), que solo se listen artículos publicados y el estado vacío. |
| `ArticleDetailViewTests` | HTTP 200/404, protección de borradores y **escapado automático del HTML crudo del `body`**. |
| `CategoryListViewTests` | HTTP 200/404, filtrado por categoría y exclusión de los artículos no publicados. |
| `UrlResolutionTests` | Que el conversor `<slug:slug>` no acepte rutas con espacios (HTTP 404). |

Las pruebas de escapado son la comprobación automática del Paso 12:

```python
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
```

---

## Conclusiones

1. El motor de plantillas de Django permite construir un portal completo
   separando con claridad la presentación del código: las vistas deciden *qué*
   se muestra y las plantillas deciden *cómo*.

2. La herencia de plantillas junto con los fragmentos reutilizables reduce de
   forma notable el HTML duplicado; en este proyecto la misma tarjeta de noticia
   sirve a la portada y al listado por categoría sin repetir una línea.

3. El uso sistemático de `{% url %}` y `{% static %}` elimina las rutas escritas
   a mano, de modo que reorganizar la aplicación no rompe ninguna plantilla.

4. El escapado automático es una defensa activa contra XSS: el HTML crudo del
   cuerpo de un artículo se muestra como texto y solo se interpretaría de forma
   deliberada con `|safe` o `{% autoescape off %}`, siempre sobre contenido
   confiable.

5. La combinación del admin personalizado con un comando de carga idempotente
   permite publicar y probar el portal sin editar código, y las 34 pruebas
   automatizadas confirman que la aplicación `news` convive con la aplicación
   `movies` del laboratorio anterior sin afectarla.

---

## Anexo — Capturas del sistema en funcionamiento

### 1. Estructura del proyecto en VS Code

<img width="532" height="846" alt="image" src="https://github.com/user-attachments/assets/a2d76cfa-1a47-4e76-bbc5-3c689a284fcf" />

<img width="577" height="631" alt="image" src="https://github.com/user-attachments/assets/a6132aa1-f88c-448a-804b-ecef65e3c451" />

<img width="556" height="781" alt="image" src="https://github.com/user-attachments/assets/ca65db55-7fbc-4542-a5c4-79c709c17f7e" />

<img width="581" height="797" alt="image" src="https://github.com/user-attachments/assets/efc7147f-a0e5-46a1-8599-9cb1b717d6e2" />

### Capturas de la pagina

<img width="1207" height="706" alt="image" src="https://github.com/user-attachments/assets/a07288b2-244e-4281-ba82-18f838984809" />

<img width="1210" height="616" alt="image" src="https://github.com/user-attachments/assets/82719ffd-a6a8-43a2-a4a7-647762d622c3" />

<img width="1242" height="622" alt="image" src="https://github.com/user-attachments/assets/2fce1b31-9ac9-4874-be2f-a21a4218a52b" />

<img width="1257" height="632" alt="image" src="https://github.com/user-attachments/assets/a433e443-ab06-44d3-acdb-1aab14042358" />

<img width="1227" height="622" alt="image" src="https://github.com/user-attachments/assets/db68f679-cf87-4ac6-96b2-a14ea890a63e" />

<img width="1251" height="631" alt="image" src="https://github.com/user-attachments/assets/722171eb-e6f7-4c58-9099-7fb7631c0812" />

<img width="1237" height="702" alt="image" src="https://github.com/user-attachments/assets/22f6d0d0-d035-4729-bc36-78487b7a86ae" />

<img width="1267" height="727" alt="image" src="https://github.com/user-attachments/assets/2a6e1455-eb71-42d9-8dd7-e7fa1d440c55" />

<img width="1242" height="622" alt="image" src="https://github.com/user-attachments/assets/1c284499-6af7-4928-86b5-adaee91a6d5e" />

<img width="1222" height="455" alt="image" src="https://github.com/user-attachments/assets/c94aa7d9-a789-48b6-9053-47cb88efcdfb" />

<img width="1132" height="491" alt="image" src="https://github.com/user-attachments/assets/226b1574-29ae-4504-8fae-1355b2f9d759" />

<img width="1432" height="522" alt="image" src="https://github.com/user-attachments/assets/9e02dc0d-964a-4854-9a39-bfa7df2a10b3" />

<img width="1242" height="510" alt="image" src="https://github.com/user-attachments/assets/d3c07732-85a7-4dbb-8560-12cca5d0adfa" />

<img width="1232" height="497" alt="image" src="https://github.com/user-attachments/assets/31d99445-e067-4c84-9da1-936b0a999157" />

<img width="1222" height="580" alt="image" src="https://github.com/user-attachments/assets/d566ea15-16f7-4bf9-937e-735a225f252e" />

<img width="1282" height="607" alt="image" src="https://github.com/user-attachments/assets/a8e4f8e0-075a-415b-a51e-bb45207b1882" />

<img width="1211" height="531" alt="image" src="https://github.com/user-attachments/assets/e3db1255-e73c-4e6b-9cfc-7bb2a0649038" />

<img width="1212" height="457" alt="image" src="https://github.com/user-attachments/assets/e045a8e6-7b08-41be-882c-058c5e476637" />

<img width="1212" height="526" alt="image" src="https://github.com/user-attachments/assets/0757e6c8-dd1d-4d07-88d5-3e6efbf1ebbd" />

<img width="1256" height="502" alt="image" src="https://github.com/user-attachments/assets/57d3df2b-0561-418c-a0cb-ee27d9e41734" />

<img width="1196" height="787" alt="image" src="https://github.com/user-attachments/assets/9f1aa45f-774a-4071-820a-a82bdc45afff" />

<img width="1147" height="771" alt="image" src="https://github.com/user-attachments/assets/df2e6f74-7a6e-4305-9e7d-e9bcf42463af" />

<img width="1155" height="672" alt="image" src="https://github.com/user-attachments/assets/74b75d94-c52b-412c-a39b-158fbb9895dd" />

<img width="1215" height="621" alt="image" src="https://github.com/user-attachments/assets/80586d4e-843a-4d4c-8e2a-d9f45ff10456" />

<img width="1217" height="547" alt="image" src="https://github.com/user-attachments/assets/eedd577c-bcb3-4eee-b00f-32dea560efc8" />

<img width="1162" height="502" alt="image" src="https://github.com/user-attachments/assets/b31935f4-cbb8-40db-b879-f1e296452b47" />

<img width="1117" height="440" alt="image" src="https://github.com/user-attachments/assets/376ce735-8d50-40d4-86a1-d17ad79ca5bd" />

<img width="1002" height="552" alt="image" src="https://github.com/user-attachments/assets/550c78e2-dab9-4002-bc95-5d4740c6f5f3" />

<img width="1216" height="455" alt="image" src="https://github.com/user-attachments/assets/f7a90f42-8775-4489-a7c8-fb3431bef861" />

<img width="1212" height="657" alt="image" src="https://github.com/user-attachments/assets/69a1ef14-d71c-40a4-b1fd-b581664593fe" />

<img width="1142" height="511" alt="image" src="https://github.com/user-attachments/assets/b323aa94-f51a-425a-9b03-d4d1e95233da" />

<img width="1242" height="481" alt="image" src="https://github.com/user-attachments/assets/9e0313e9-c32c-4871-9260-3a96d6398833" />

<img width="1297" height="611" alt="image" src="https://github.com/user-attachments/assets/862770d7-d1ce-4add-9645-72f00f5452bf" />

<img width="1217" height="712" alt="image" src="https://github.com/user-attachments/assets/7052f9cb-bb3d-40ef-a0be-a6b59090b756" />

<img width="1187" height="627" alt="image" src="https://github.com/user-attachments/assets/1f47cdf7-f5c3-4418-86cb-586e99c3e169" />

<img width="961" height="515" alt="image" src="https://github.com/user-attachments/assets/41764eb4-c394-44ba-98c3-749330e73469" />

<img width="1100" height="520" alt="image" src="https://github.com/user-attachments/assets/25928b0c-8d8a-467c-a366-cb7c9db38651" />

<img width="1172" height="582" alt="image" src="https://github.com/user-attachments/assets/8bce3f71-b8be-41ba-86c3-6ad59a0305dc" />

<img width="1057" height="580" alt="image" src="https://github.com/user-attachments/assets/f49cb4d8-9d63-4357-a931-e4e2ecc760ab" />

<img width="1140" height="536" alt="image" src="https://github.com/user-attachments/assets/3794cdd6-bf65-44f3-a42d-1e28def8707b" />

<img width="1212" height="592" alt="image" src="https://github.com/user-attachments/assets/e1147da0-5a0c-4cb1-bdf0-56ce8eba7a95" />

<img width="1195" height="667" alt="image" src="https://github.com/user-attachments/assets/672f4fa2-38bf-423f-9376-9f7e3ee60404" />

<img width="1041" height="320" alt="image" src="https://github.com/user-attachments/assets/878d922c-bdc5-4316-ba25-91212c284505" />

<img width="837" height="420" alt="image" src="https://github.com/user-attachments/assets/1370e690-98fa-4b9b-873f-b36edc09d860" />

<img width="1142" height="667" alt="image" src="https://github.com/user-attachments/assets/78bf95f9-3d8c-4476-b7b6-3876cb8bb87b" />

<img width="1202" height="701" alt="image" src="https://github.com/user-attachments/assets/f9dec56f-86f6-43b0-8a1a-a8415386a4c5" />

















































