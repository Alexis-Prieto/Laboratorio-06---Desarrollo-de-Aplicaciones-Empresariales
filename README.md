# Labs 05 y 06 — Administrador y motor de plantillas con Django (TECSUP)

Proyecto con dos entregas sobre el mismo repositorio:

- **Lab 05** — panel de administración de Django aplicado a un catálogo de
  películas: modelos relacionados, `ModelAdmin` personalizado, `Inline`, campos
  de auditoría de solo lectura, control de acceso por grupos y permisos, y una
  vista pública de recomendaciones.
- **Lab 06** — motor de plantillas de Django aplicado a un portal de noticias:
  herencia con `base.html`, fragmento reutilizable `_article_card.html`, tags de
  control, filtros, archivos estáticos y demostración del escapado automático.

> **Modalidad:** trabajo **individual**. Todo el contenido fue desarrollado por
> un único estudiante, sin reparto de roles.

---

## 1. Requisitos previos

- Python 3.12 o superior
- Git (opcional)

## 2. Instalación

```powershell
# Crear el entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar las dependencias
pip install -r requirements.txt
```

## 3. Configuración

El proyecto **no** contiene credenciales escritas a mano. La clave secreta y el
modo de depuración se leen del archivo `.env` mediante `python-dotenv`.

```powershell
# Windows PowerShell
copy .env.example .env
```

Si `.env` no existe, `settings.py` funciona con valores de desarrollo por
defecto, pero se recomienda crearlo antes de ejecutar el proyecto.

## 4. Puesta en marcha

```powershell
python manage.py migrate
python manage.py seed_data
python manage.py setup_groups
python manage.py seed_news
python manage.py createsuperuser
python manage.py runserver
```

- Portal de noticias (Lab 06): <http://127.0.0.1:8000/>
- Panel de administración: <http://127.0.0.1:8000/admin/>
- Vista pública de recomendaciones (Lab 05): <http://127.0.0.1:8000/recommendations/1/>

## 5. Comandos de gestión

| Comando | Descripción |
| --- | --- |
| `python manage.py seed_data` | Crea 4 géneros, 6 personas, 10 películas y sus valoraciones. Es idempotente: se puede volver a ejecutar sin duplicar registros. |
| `python manage.py seed_news` | Crea 3 categorías, 3 autores y 6 artículos del portal de noticias. También es idempotente. |
| `python manage.py setup_groups` | Crea los grupos `editores` y `lectores` con sus permisos, y el usuario `editor_demo`. |
| `python manage.py dumpdata movies --indent 2 --output fixtures/test_data.json` | Exporta los datos a un fixture. |
| `python manage.py loaddata fixtures/test_data.json` | Restaura el fixture. |

## 6. Usuarios de demostración

| Usuario | Contraseña | Permisos |
| --- | --- | --- |
| `admin` | `Admin12345!` | Superusuario: acceso total. |
| `editor_demo` | `Editor12345!` | Grupo `editores`: añadir y cambiar películas, **sin eliminar**. |

> Estas credenciales son únicamente para el desarrollo local. Deben cambiarse
> antes de cualquier despliegue real.

## 7. Estructura del proyecto

```
proyecto_cine/
├── config/            # Configuración del proyecto (settings, urls, wsgi, asgi)
├── movies/            # App del Lab 05: catálogo de películas y su panel
│   ├── admin.py       # ModelAdmin, Inline y campos de solo lectura
│   ├── models.py      # Movie, Genre, Person, Rating
│   ├── views.py       # Vista pública de recomendaciones
│   ├── urls.py        # Rutas de la aplicación
│   ├── management/commands/  # seed_data y setup_groups
│   └── tests.py       # Pruebas automáticas
├── news/              # App del Lab 06: portal de noticias
│   ├── admin.py       # ModelAdmin de Author, Category y Article
│   ├── models.py      # Author, Category, Article
│   ├── views.py       # home, article_detail y category_list
│   ├── urls.py        # Rutas con app_name = 'news'
│   ├── management/commands/  # seed_news
│   └── tests.py       # Pruebas automáticas
├── templates/         # Plantillas globales (DIRS)
│   ├── base.html      # Plantilla base con bloques
│   ├── partials/      # Fragmentos reutilizables (_article_card.html)
│   └── news/          # home, article_detail y category_list
├── fixtures/          # Datos de prueba exportados
├── media/             # Archivos subidos (pósteres, fotos y artículos)
└── static/            # Archivos estáticos (news/css/style.css)
```

## 8. Pruebas

```powershell
python manage.py test news movies
```

## 9. Buenas prácticas aplicadas

- Modelos en **singular** y una aplicación por responsabilidad.
- Código y comentarios en **inglés**; documentación en **español**.
- PEP 8 y *docstrings* en todas las clases y funciones públicas.
- Sin credenciales en `settings.py`: se usan variables de entorno.
- Migraciones versionadas dentro del repositorio.
- `.gitignore` que excluye `venv/`, `.env`, `db.sqlite3` y archivos cargados.
