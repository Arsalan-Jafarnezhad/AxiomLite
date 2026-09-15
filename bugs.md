Configuration analysis — bugs and issues found
Analysis of configuration/ complete. Below are verified issues, grouped by severity, each tied to the file and line I read. No files were changed.

Critical — crashes at startup or runtime
1. Dev-only packages loaded unconditionally debug_toolbar, django_extensions and the debug-toolbar middleware at settings.py:158 are always loaded, but both packages exist only in requirements/development.txt — absent from base.txt and production.txt. Production boot via build.sh fails with ModuleNotFoundError.

2. unfold.contrib.import_export with no django-import-export settings.py:147 imports that submodule; no import-export package is in any requirement file. App loading fails.

3. Registration 500 — ambiguous backend on login() SignUpView.form_valid() calls login(self.request, self.object) on a user created by a plain AccountSignUpForm. With two backends in AUTHENTICATION_BACKENDS, Django raises ValueError rather than guessing. Needs an explicit backend argument.

4. reverse("shop:payment-internal") has no matching namespace payment_gateway.py:89 reverses a shop: namespace that is never registered (urls.py:6 exposes only core/accounts/catalog/weblog/questions). Non-Zarinpal currencies raise NoReverseMatch; payment_internal.html is unreachable.

5. Missing ZARINPAL_MERCHANT_ID setting Read at payment_gateway.py:119 and payment_gateway.py:162; defined nowhere in settings.py or .env.sample.

6. Markdown widgets reverse an unregistered URL name weblog/widgets/markdown.py:26 and questions/widgets.py:11 call reverse("weblog:articles-upload-image"), but the router in weblog/api/urls.py sets no app_name/namespace (included bare at weblog/urls/api.py:4). Every form rendering these widgets raises NoReverseMatch.

7. pricing app is orphaned and internally conflicted Not in LOCAL_APPS, no URL include, yet plan.py:136 reverses a nonexistent pricing:plan-detail. It ships both models.py and a models/ package defining overlapping names (PricingPlan/Feature vs Plan/PlanFeature); loading both raises a conflicting-model RuntimeError.

High — incorrect behavior
8. Soft-delete defeated for User — User.objects = UserManager() extends a plain QuerySet, not SoftDeleteQuerySet. Soft-deleted users remain visible and can still authenticate; .all().delete() hard-deletes.

9. Soft-delete breaks Django's delete() contract — SoftDeleteQuerySet.delete() returns an int, not (count, {label: n}); SoftDeleteModel.delete() returns None and emits no delete signals/cascade, so django-cleanup never removes orphaned files.

10. Dashboard counters wrong — DashboardView sets every status count to the same articles.all().count(); author filter commented out; total_comments filters by author (dashboard.py:54) so superusers see 0.

11. Tests reverse nonexistent names — weblog-api:article-list (test_api.py:37), weblog:article-list (test_views.py:65) and weblog:dashboard (test_views.py:296) are all unregistered.

12. Non-ISO currency in djmoney — CURRENCIES = ("USD","EUR","IRT"); IRT is not ISO 4217 (IRR is).

13. Axes lockout effectively off — AXES_COOLOFF_TIME = timedelta(seconds=1) releases a lockout after one second.

14. Email verification configured but unused — ACCOUNT_EMAIL_VERIFICATION is bypassed by the custom SignUpView.

15. next dropped on login — SignInView.get_success_url() hard-codes core:index.

Medium
STATIC_URL defaults to "static/" with no leading slash (vs "/media/").
CSRF_COOKIE_HTTPONLY = True conflicts with cookie-based AJAX in SignOutView.
Duplicate submit route and slug shadowing /questions/api/ in questions/urls/__init__.py.
structure.py:7 opens structure.txt at import and blocks on input().
Email uniqueness is case-sensitive (forms.py:93, user.py:42), so A@x.com and a@x.com can coexist.
drf_spectacular configured (settings.py:415) but no schema/Swagger route in urls.py.
Redis cache mandatory at settings.py:452; errors when no Redis runs.
base.txt has no version pins; whitenoise is missing from dev requirements though it is the default static backend.
QUESTIONS_EXECUTION_BACKEND = "docker" requires a Docker daemon; QUESTIONS_SANITIZE_MARKDOWN = False leaves Markdown unsanitized.
Profile.__str__ triggers a lazy user fetch (N+1); missing_profile_items omits items counted by completion_percent.
Unused imports in context_processors.py:2 and core/views.py:3; SignOutView greets anonymous users as "Goodbye, .".
Suggested fix order
Make debug-only apps/middleware conditional on DEBUG; add django-import-export or drop the unfold submodule.
Register shop:payment-internal (or drop the namespace) and give the weblog API router a namespace, or strip the weblog: prefix from both widgets.
Pass an explicit backend to login() and cover registration with a test.
Route User.objects through the soft-delete manager and restore delete() return value/signals.
Fix the dashboard counters and the broken reverse() names in the test suite, then run it.
Decide pricing's fate (install + migrate, or delete the shadowed models.py).
Address ZARINPAL_MERCHANT_ID, the IRT currency, Axes cooloff, STATIC_URL, CSRF/HttpOnly, and pin requirements.
Verification note: items 3, 8 and 9 follow from Django's documented login(), QuerySet.delete() and signal behavior; confirm by running python configuration/manage.py test accounts weblog questions plus a real registration request. I could not execute the suite in this session, so those three are reasoned from the code and the framework contract rather than observed test output.