"""Management command that loads sample news content.

The command is idempotent: running it several times does not duplicate
categories, authors or articles. Everything runs inside a single transaction,
so a failure leaves the database untouched.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from news.models import Article, Author, Category

CATEGORIES = [
    (
        'Tecnología',
        'Avances, lanzamientos y tendencias del mundo digital.',
    ),
    (
        'Ciencia',
        'Descubrimientos y estudios explicados para todo público.',
    ),
    (
        'Cultura',
        'Arte, literatura, cine y vida social de nuestra región.',
    ),
]

AUTHORS = [
    (
        'Ana Torres',
        'Periodista especializada en tecnología y transformación digital.',
    ),
    (
        'Luis Ramírez',
        'Divulgador científico con quince años de experiencia en radio.',
    ),
    (
        'Sofía Delgado',
        'Editora de cultura y crítica de arte contemporáneo.',
    ),
]

ARTICLES = [
    {
        'title': 'Inteligencia artificial en las aulas peruanas',
        'summary': (
            'Universidades y colegios empiezan a usar asistentes de '
            'inteligencia artificial para personalizar el aprendizaje y '
            'detectar dificultades a tiempo.'
        ),
        'author': 'Ana Torres',
        'categories': ['Tecnología'],
        'days_ago': 2,
        'body': (
            'La inteligencia artificial dejó de ser una promesa lejana en '
            'las aulas peruanas. Varias universidades de Lima ya prueban '
            'asistentes que responden preguntas de los estudiantes fuera del '
            'horario de clase y sugieren ejercicios según su desempeño.\n\n'
            'Los docentes consultados coinciden en que la herramienta no '
            'reemplaza la labor del profesor, pero sí libera tiempo de '
            'tareas repetitivas como la corrección de ejercicios básicos.\n\n'
            'El principal desafío sigue siendo la formación del profesorado y '
            'el acceso a una conexión estable en las zonas rurales.'
        ),
    },
    {
        'title': 'Cinco hábitos para proteger tus datos personales',
        'summary': (
            'Contraseñas largas, verificación en dos pasos y revisiones '
            'periódicas de permisos reducen de forma notable el riesgo de '
            'sufrir un robo de información.'
        ),
        'author': 'Ana Torres',
        'categories': ['Tecnología'],
        'days_ago': 9,
        'raw_html': True,
        'body': (
            '<p>Este es un <strong>párrafo importante</strong> de prueba.</p>'
            '<p>El contenido de este artículo se guardó con etiquetas HTML '
            'reales para demostrar el escapado automático de Django.</p>'
        ),
    },
    {
        'title': 'Nuevo estudio sobre el agua en Marte',
        'summary': (
            'Un equipo internacional encontró depósitos de hielo bajo la '
            'superficie marciana, un hallazgo que reabre el debate sobre la '
            'posibilidad de vida microbiana.'
        ),
        'author': 'Luis Ramírez',
        'categories': ['Ciencia'],
        'days_ago': 4,
        'body': (
            'Un equipo internacional de investigadores publicó un estudio '
            'que describe depósitos de hielo de agua a pocos metros bajo la '
            'superficie de Marte.\n\n'
            'Los datos provienen de un radar instalado en una sonda orbital '
            'y fueron comparados con mediciones similares realizadas en la '
            'Antártida.\n\n'
            'Los autores advierten que el hallazgo no confirma la existencia '
            'de vida, pero mejora las expectativas de futuras misiones '
            'tripuladas.'
        ),
    },
    {
        'title': 'Cómo el sueño reordena la memoria',
        'summary': (
            'Dormir bien no solo descansa el cuerpo: durante la noche el '
            'cerebro clasifica lo aprendido y descarta la información '
            'irrelevante.'
        ),
        'author': 'Luis Ramírez',
        'categories': ['Ciencia'],
        'days_ago': 14,
        'body': (
            'Durante el sueño profundo el cerebro reproduce los patrones de '
            'actividad que se registraron durante el día, como si ensayara '
            'lo aprendido.\n\n'
            'Ese proceso, conocido como consolidación, explica por qué '
            'estudiar antes de dormir suele dar mejores resultados que '
            'estudiar después de una noche sin descanso.\n\n'
            'Los especialistas recomiendan mantener horarios regulares y '
            'evitar las pantallas durante la última media hora del día.'
        ),
    },
    {
        'title': 'El festival de cine independiente vuelve a las salas',
        'summary': (
            'La nueva edición del festival reunirá veinte películas de '
            'directores emergentes y abrirá una sección dedicada al cine '
            'documental regional.'
        ),
        'author': 'Sofía Delgado',
        'categories': ['Cultura'],
        'days_ago': 6,
        'body': (
            'El festival de cine independiente confirmó su nueva edición con '
            'una selección de veinte largometrajes de directores '
            'emergentes.\n\n'
            'La programación incluye una sección dedicada al documental '
            'regional, con trabajos rodados en Cusco, Iquitos y Arequipa.\n\n'
            'Las funciones se realizarán en salas alternativas y contarán '
            'con conversatorios abiertos con parte del equipo de cada '
            'película.'
        ),
    },
    {
        'title': 'La novela gráfica peruana gana terreno',
        'summary': (
            'Editoriales locales publican cada vez más historietas de autor '
            'y las ferias del libro les dedican mesas propias. El público '
            'joven responde.'
        ),
        'author': 'Sofía Delgado',
        'categories': ['Cultura'],
        'days_ago': 21,
        'body': (
            'La novela gráfica dejó de ser un género marginal en las '
            'librerías peruanas. Varias editoriales locales confirmaron '
            'nuevas colecciones de autor para este año.\n\n'
            'Las ferias del libro también reflejan el cambio: la mayoría '
            'reservó mesas específicas para historietas y talleres de '
            'dibujo.\n\n'
            'Los libreros señalan que el público joven es el principal '
            'responsable de este crecimiento sostenido.'
        ),
    },
]


class Command(BaseCommand):
    """Create the sample categories, authors and articles."""

    help = 'Load 3 categories, 3 authors and 6 sample articles.'

    @transaction.atomic
    def handle(self, *args, **options):
        """Create the sample content, reusing the records that exist."""
        categories = {}
        for name, description in CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': description,
                },
            )
            categories[name] = category
            verb = 'Created' if created else 'Found'
            self.stdout.write(f'{verb} category: {category.name}')

        authors = {}
        for name, bio in AUTHORS:
            author, created = Author.objects.get_or_create(
                name=name,
                defaults={'bio': bio},
            )
            authors[name] = author
            verb = 'Created' if created else 'Found'
            self.stdout.write(f'{verb} author: {author.name}')

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
            verb = 'Created' if created else 'Found'
            self.stdout.write(f'{verb} article: {article.title}')
            if data.get('raw_html'):
                self.stdout.write(
                    f'  -> {article.slug} stores raw HTML to demonstrate '
                    'the automatic escaping (step 12).'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed finished: {Category.objects.count()} categories, '
                f'{Author.objects.count()} authors, '
                f'{Article.objects.count()} articles.'
            )
        )