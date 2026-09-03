# AxiomLite

<p align="center">
  <strong>A modern, modular Django web platform with authentication, catalog management, blogging, REST APIs, and an online code-execution system.</strong>
</p>

<p align="center">
  <a href="https://github.com/Arsalan-Jafarnezhad/AxiomLite">
    <img src="https://img.shields.io/badge/GitHub-AxiomLite-181717?logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-6.x-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/Django%20REST%20Framework-API-A30000?logo=django&logoColor=white" alt="Django REST Framework">
  <img src="https://img.shields.io/badge/Tailwind%20CSS-4.x-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/DaisyUI-5.x-5A0EF8?logo=daisyui&logoColor=white" alt="DaisyUI">
  <img src="https://img.shields.io/badge/PostgreSQL-Ready-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-Supported-DC382D?logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Celery-Task%20Queue-37814A?logo=celery&logoColor=white" alt="Celery">
  <img src="https://img.shields.io/badge/Docker-Sandbox-2496ED?logo=docker&logoColor=white" alt="Docker">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/Arsalan-Jafarnezhad/AxiomLite/main/configuration/static/images/logo.webp" alt="AxiomLite" width="120">
</p>

---

## Overview

**AxiomLite** is a modular web platform built with Django.

The project combines several systems that are commonly required by modern web applications:

* User authentication and profiles
* Account management
* Product and category management
* Orders and order items
* Discount codes
* Payment records
* Product comments
* Technical specifications
* Weblog / article management
* REST APIs
* Online programming questions
* Code submissions
* Sandboxed code execution
* Background task processing
* Redis integration
* PostgreSQL support
* Object storage support
* Responsive frontend styling with Tailwind CSS and DaisyUI

The project is designed around a modular Django application structure so that individual systems can evolve independently.

---

## ✨ Features

### 👤 Authentication & Accounts

AxiomLite provides a dedicated accounts application with:

* Sign in
* Sign up
* Sign out
* Account dashboard
* Account editing
* Account details
* Public user profiles
* Django Allauth integration

Available account routes include:

```text
/accounts/
/accounts/sign-in/
/accounts/sign-up/
/accounts/sign-out/
/accounts/account/
/accounts/account/edit/
/accounts/account/detail/
/accounts/profiles/<username>/
```

---

### 🛍️ Catalog

The catalog system provides a complete foundation for managing products and commerce-related entities.

#### Categories

* Category listing
* Category creation
* Category details
* Category editing
* Category deletion

```text
/catalog/
/catalog/categories/
/catalog/categories/add/
/catalog/categories/<slug>/
/catalog/categories/<slug>/edit/
/catalog/categories/<slug>/delete/
```

#### Products

* Product listing
* Product creation
* Product details
* Product editing
* Product deletion
* Lightweight panel/detail endpoint

```text
/catalog/products/
/catalog/products/add/
/catalog/products/<slug>/
/catalog/products/<slug>/panel/
/catalog/products/<slug>/edit/
/catalog/products/<slug>/delete/
```

#### Product Comments

```text
/catalog/comments/
/catalog/comments/add/
/catalog/comments/<id>/
/catalog/comments/<id>/edit/
/catalog/comments/<id>/delete/
```

#### Orders

```text
/catalog/orders/
/catalog/orders/add/
/catalog/orders/<order_id>/
/catalog/orders/<order_id>/panel/
/catalog/orders/<order_id>/edit/
/catalog/orders/<order_id>/delete/
/catalog/orders/<order_id>/transition/<action>/
```

#### Order Items

```text
/catalog/order-items/
/catalog/order-items/add/
/catalog/order-items/<id>/
/catalog/order-items/<id>/edit/
/catalog/order-items/<id>/delete/
```

#### Discount Codes

```text
/catalog/offcodes/
/catalog/offcodes/add/
/catalog/offcodes/<id>/
/catalog/offcodes/<id>/edit/
/catalog/offcodes/<id>/delete/
```

#### Payments

Payments are exposed as records and are intended to be created by the checkout flow.

```text
/catalog/payments/
/catalog/payments/<payment_id>/
/catalog/payments/<payment_id>/panel/
/catalog/payments/<payment_id>/edit/
/catalog/payments/<payment_id>/delete/
```

#### Specifications

The catalog also supports configurable product specifications:

```text
/catalog/specs/<spec_type>/
/catalog/specs/<spec_type>/add/
/catalog/specs/<spec_type>/<id>/
/catalog/specs/<spec_type>/<id>/edit/
/catalog/specs/<spec_type>/<id>/delete/
```

---

## 📝 Weblog

AxiomLite contains a dedicated weblog application for publishing and managing articles.

The weblog system is separated into its own Django application and follows a modular architecture containing models, forms, selectors, services, permissions, API components, signals, and static assets.

Main entry point:

```text
/weblog/
```

The application is designed to support a structured publishing workflow rather than treating blog posts as simple database records.

---

## 💻 Online Judge & Code Execution

One of the major components of AxiomLite is its programming-question system.

The `questions` application contains:

* Questions
* Programming languages
* Tags
* Difficulty levels
* Test cases
* Submissions
* Automatic evaluation
* Execution management
* Submission results
* REST API endpoints
* Docker-based execution infrastructure

The project separates the question domain from its execution layer, making the execution system easier to isolate and maintain.

### Question API

```text
/questions/
```

API endpoints include:

```text
/questions/questions/
/questions/questions/<slug>/
/questions/questions/<slug>/submissions/
/questions/submissions/
/questions/submissions/<id>/
```

These endpoints provide functionality for:

* Listing questions
* Retrieving a question
* Submitting solutions
* Listing submissions
* Inspecting individual submissions

---

## 🔐 Sandboxed Code Execution

AxiomLite uses Docker for executing submitted code instead of directly executing untrusted programs on the Django host.

The execution subsystem is designed around container isolation and resource restrictions.

The executor uses restrictions such as:

* No network access
* Read-only filesystem
* Temporary filesystem for `/tmp`
* CPU limits
* Memory limits
* Process limits
* Dropped Linux capabilities
* `no-new-privileges`
* Non-root execution
* Execution timeouts
* Output-size limits
* Automatic container cleanup

This architecture provides a significantly safer execution model than running submitted source code directly through Python's `subprocess` on the application server.

> **Security note:** No sandbox should automatically be considered perfectly secure. Running arbitrary code requires continuous security auditing, host hardening, container updates, and careful operational isolation.

---

# 🧱 Architecture

AxiomLite is organized into multiple Django applications.

```text
AxiomLite/
│
├── configuration/
│   │
│   ├── configuration/
│   │   ├── settings/
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── accounts/
│   ├── catalog/
│   ├── core/
│   ├── questions/
│   └── weblog/
│
├── scripts/
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── build.sh
├── package.json
├── package-lock.json
└── README.md
```

The Django project entry point is:

```text
configuration/manage.py
```

and Django uses:

```text
configuration.settings
```

as its settings module.

---

# 🛠️ Technologies

## Backend

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/DRF-A30000?logo=django&logoColor=white" alt="Django REST Framework">
</p>

* Python
* Django
* Django REST Framework
* Django Allauth
* Django Filter
* Django Extensions
* Django Crispy Forms
* Django Debug Toolbar
* Django Simple History
* Django MPTT
* Django Parler
* Django Money
* Django Storages
* Django Redis
* Django Ratelimit
* Django Axes
* DRF Spectacular

---

## Database

<p>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
</p>

The project supports PostgreSQL through:

```text
psycopg
dj-database-url
```

SQLite can also be useful during local development depending on the project's settings configuration.

---

## Background Processing

<p>
  <img src="https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white" alt="Celery">
  <img src="https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white" alt="Redis">
</p>

AxiomLite includes:

* Celery
* Redis
* Django Celery Beat
* Django Celery Results
* Django Redis

These components provide the foundation for asynchronous and scheduled background tasks.

---

## Frontend

<p>
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/DaisyUI-5A0EF8?logo=daisyui&logoColor=white" alt="DaisyUI">
  <img src="https://img.shields.io/badge/Material_Symbols-757575?logo=materialdesignicons&logoColor=white" alt="Material Symbols">
  <img src="https://img.shields.io/badge/Prism.js-2D2D2D?logo=prism&logoColor=white" alt="Prism.js">
</p>

The frontend stack includes:

* Tailwind CSS
* DaisyUI
* Material Symbols
* Prism.js
* Native JavaScript
* Django Templates

Frontend dependencies are managed through `npm`.

---

## Infrastructure

<p>
  <img src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=white" alt="Gunicorn">
  <img src="https://img.shields.io/badge/Uvicorn-499848?logo=uvicorn&logoColor=white" alt="Uvicorn">
</p>

Production-oriented components include:

* Docker
* Gunicorn
* Uvicorn
* WhiteNoise
* Sentry
* AWS S3 / compatible object storage through `boto3` and `django-storages`

---

# 📦 Requirements

Python dependencies are separated by environment:

```text
requirements/
├── base.txt
├── development.txt
└── production.txt
```

### Base

Contains the dependencies required by the application itself.

### Development

Includes the base dependencies plus development tools such as:

* Pytest
* Pytest-Django
* Model Bakery
* Pylint
* Pylint-Django
* Isort
* Djlint
* Django Debug Toolbar
* Django Extensions
* Build tools

### Production

Includes the base dependencies plus deployment-related packages such as:

* Gunicorn
* Uvicorn
* WhiteNoise
* Sentry SDK

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/Arsalan-Jafarnezhad/AxiomLite.git
cd AxiomLite
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Python dependencies

For development:

```bash
pip install -r requirements/development.txt
```

For production:

```bash
pip install -r requirements/production.txt
```

---

# 🎨 Frontend Setup

Install Node dependencies:

```bash
npm install
```

The project's frontend package configuration includes:

* Tailwind CSS CLI
* DaisyUI
* Material Symbols
* Prism.js

The existing npm scripts provide CSS development and production builds.

### Development CSS watcher

```bash
npm run dev:css
```

### Production CSS build

```bash
npm run build:css
```

### Copy Material Symbols

```bash
npm run icons:copy
```

---

# ⚙️ Environment Configuration

Create an environment file for local configuration.

For example:

```text
.env
```

Typical configuration may include:

```env
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=sqlite:///db.sqlite3

REDIS_URL=redis://127.0.0.1:6379/1
```

For production, use strong secrets and configure your database, cache, email, storage, and security settings appropriately.

> Never commit `.env` files or production credentials to Git.

---

# 🗄️ Database Setup

Run migrations:

```bash
python configuration/manage.py migrate
```

Create an administrator:

```bash
python configuration/manage.py createsuperuser
```

---

# ▶️ Run the Development Server

```bash
python configuration/manage.py runserver
```

The application will normally be available at:

```text
http://127.0.0.1:8000/
```

---

# 🔄 Celery & Redis

If background processing is enabled, start Redis first.

Then run a Celery worker:

```bash
celery -A configuration worker -l INFO
```

For scheduled tasks, run Celery Beat:

```bash
celery -A configuration beat -l INFO
```

The exact process configuration can be adapted to the deployment environment.

---

# 🐳 Docker

The question execution system contains Docker-specific infrastructure for running submitted programs inside isolated containers.

Make sure Docker is installed and running before using the execution functionality.

Verify Docker:

```bash
docker --version
```

Verify that Docker can start containers:

```bash
docker run --rm hello-world
```

The executor itself is located under:

```text
configuration/questions/docker/
configuration/questions/execution/
```

---

# 🔗 URL Map

The primary URL configuration exposes the following application areas:

| Area      | URL           |
| --------- | ------------- |
| Home      | `/`           |
| Admin     | `/admin/`     |
| Accounts  | `/accounts/`  |
| Catalog   | `/catalog/`   |
| Weblog    | `/weblog/`    |
| Questions | `/questions/` |

### Account URLs

```text
/accounts/
/accounts/sign-in/
/accounts/sign-up/
/accounts/sign-out/
/accounts/account/
/accounts/account/edit/
/accounts/account/detail/
/accounts/profiles/<username>/
```

### Catalog URLs

```text
/catalog/
/catalog/categories/
/catalog/products/
/catalog/comments/
/catalog/orders/
/catalog/order-items/
/catalog/offcodes/
/catalog/payments/
/catalog/specs/<spec_type>/
```

### Questions API

```text
/questions/questions/
/questions/questions/<slug>/
/questions/questions/<slug>/submissions/
/questions/submissions/
/questions/submissions/<id>/
```

---

# 🔌 API

AxiomLite includes a REST API layer powered by Django REST Framework.

The questions API currently exposes:

### List Questions

```http
GET /questions/questions/
```

### Retrieve Question

```http
GET /questions/questions/<slug>/
```

### Submit Solution

```http
POST /questions/questions/<slug>/submissions/
```

### List Submissions

```http
GET /questions/submissions/
```

### Retrieve Submission

```http
GET /questions/submissions/<id>/
```

The underlying API URL configuration defines these question and submission endpoints directly.

---

# 📖 API Documentation

The project includes `drf-spectacular`, allowing the REST API to be documented through OpenAPI.

When API documentation routes are enabled in the deployment configuration, they can be exposed through the configured schema/documentation endpoints.

---

# 🧪 Testing

Run the Django test suite with:

```bash
pytest
```

Or:

```bash
python -m pytest
```

For Django's built-in test runner:

```bash
python configuration/manage.py test
```

---

# 🔍 Code Quality

Development tooling includes:

```text
pylint
pylint-django
isort
djlint
pytest
pytest-django
```

Example:

```bash
pylint configuration/
```

```bash
isort configuration/
```

```bash
djlint configuration/ --check
```

---

# 🏗️ Build

The repository includes a build script:

```bash
./build.sh
```

On Linux/macOS, make it executable if necessary:

```bash
chmod +x build.sh
```

The frontend build can also be generated independently:

```bash
npm run build:css
```

---

# 📁 Project Structure

A simplified representation of the project:

```text
AxiomLite/
│
├── configuration/
│   │
│   ├── configuration/
│   │   ├── settings/
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── accounts/
│   │   ├── models/
│   │   ├── views/
│   │   ├── forms/
│   │   └── urls.py
│   │
│   ├── catalog/
│   │   ├── models/
│   │   ├── views/
│   │   ├── forms/
│   │   └── urls.py
│   │
│   ├── core/
│   │
│   ├── questions/
│   │   ├── api/
│   │   ├── docker/
│   │   ├── execution/
│   │   ├── forms/
│   │   ├── models/
│   │   ├── management/
│   │   ├── selectors/
│   │   └── services/
│   │
│   └── weblog/
│       ├── api/
│       ├── models/
│       ├── forms/
│       ├── selectors/
│       ├── services/
│       ├── permissions.py
│       └── signals.py
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── scripts/
│
├── build.sh
├── package.json
├── package-lock.json
├── .gitignore
└── README.md
```

---

# 🧩 Design Principles

AxiomLite follows several architectural principles:

### Modular Django Applications

Each major domain is isolated into its own Django application.

```text
accounts
catalog
core
questions
weblog
```

This makes the project easier to maintain and extend.

### Separation of Concerns

The project makes use of separate layers such as:

```text
Models
Views
Forms
Selectors
Services
Permissions
APIs
Execution
```

This avoids putting all business logic inside Django views.

### API-First Components

Systems such as the question engine expose dedicated API endpoints rather than relying exclusively on HTML views.

### Isolated Code Execution

User-submitted source code is treated as untrusted input and executed through Docker-based isolation.

### Environment-Specific Dependencies

Dependencies are separated into:

```text
base
development
production
```

which keeps deployment environments cleaner.

---

# 🔒 Security

Security-sensitive functionality is treated as a first-class concern.

AxiomLite includes tools and components for:

* Authentication
* Login protection
* Rate limiting
* Account security
* CSRF protection
* Security middleware
* Session management
* Sentry monitoring
* Container isolation for submitted code

Relevant packages include:

```text
django-axes
django-ratelimit
django-security-hunter
sentry-sdk
```

For production deployment, additionally configure:

* HTTPS
* Secure cookies
* Strong `SECRET_KEY`
* Correct `ALLOWED_HOSTS`
* Restricted CORS
* Secure database credentials
* Production `DEBUG=False`
* Proper proxy configuration
* Container/host isolation
* Regular dependency updates

---

# 🚢 Production

A typical production stack can be structured as:

```text
                    ┌───────────────┐
                    │    Browser    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Reverse Proxy │
                    │  HTTPS / TLS  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Gunicorn    │
                    │    Django     │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       ┌──────────┐   ┌──────────┐   ┌───────────┐
       │PostgreSQL│   │  Redis   │   │  Storage  │
       └──────────┘   └────┬─────┘   └───────────┘
                           │
                           ▼
                    ┌───────────────┐
                    │    Celery     │
                    │    Workers    │
                    └───────────────┘

                    ┌───────────────┐
                    │ Docker Judge  │
                    │  Containers   │
                    └───────────────┘
```

Production dependencies include:

```text
gunicorn
uvicorn
whitenoise
sentry-sdk
```

---

# 🧰 Useful Management Commands

### Create migrations

```bash
python configuration/manage.py makemigrations
```

### Apply migrations

```bash
python configuration/manage.py migrate
```

### Create superuser

```bash
python configuration/manage.py createsuperuser
```

### Collect static files

```bash
python configuration/manage.py collectstatic
```

### Check the project

```bash
python configuration/manage.py check
```

### Run development server

```bash
python configuration/manage.py runserver
```

---

# 🌐 Static & Media Files

During development, Django serves static and media files according to the configured settings.

The main URL configuration enables development-time static and media serving when:

```python
DEBUG = True
```

Production deployments should use a proper static/media strategy such as:

* WhiteNoise for static assets
* S3-compatible object storage for media
* CDN/object storage where appropriate

---

# 📊 Monitoring

AxiomLite includes Sentry support through:

```text
sentry-sdk
```

This can be used to monitor:

* Application errors
* Exceptions
* Performance problems
* Production failures

Configure Sentry through environment variables rather than committing DSNs to the repository.

---

# 🤝 Contributing

Contributions are welcome.

A good contribution workflow is:

```bash
git clone https://github.com/Arsalan-Jafarnezhad/AxiomLite.git
cd AxiomLite

git checkout -b feature/my-feature
```

Make your changes, run the relevant tests and quality checks, then commit:

```bash
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

### Before submitting a PR

Run:

```bash
python configuration/manage.py check
```

```bash
pytest
```

and, where relevant:

```bash
isort configuration/
```

```bash
pylint configuration/
```

---

# 📝 License

Add the project's license here when a license has been selected.

> Until a license is explicitly added to the repository, users should not assume that the source code is available for unrestricted redistribution or commercial use.

---

# 👨‍💻 Author

**Arsalan Jafarnezhad**

GitHub:

https://github.com/Arsalan-Jafarnezhad

Project:

https://github.com/Arsalan-Jafarnezhad/AxiomLite

---

# ⭐ Support

If AxiomLite is useful to you:

* ⭐ Star the repository
* 🐛 Report bugs through GitHub Issues
* 💡 Suggest improvements
* 🔧 Submit Pull Requests
* 📖 Improve documentation

---

# 📌 Project Status

AxiomLite is an actively developed Django project.

The architecture is intentionally modular, with the catalog, authentication, weblog, API, and online-judge components maintained as separate application domains.

---

<p align="center">
  <strong>Built with Python, Django, and a lot of engineering.</strong>
</p>

<p align="center">
  <a href="https://github.com/Arsalan-Jafarnezhad/AxiomLite">
    AxiomLite
  </a>
</p>
