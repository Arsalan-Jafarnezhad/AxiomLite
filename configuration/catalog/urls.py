"""
catalog/urls.py

Include this in your project urls.py with:

    path("catalog/", include("catalog.urls", namespace="catalog")),

Note: Product/Order/Payment already expose ``panel_url`` / ``absolute_url``
properties on the model pointing at ``catalog:product-detail-panel`` etc.
Those "panel" endpoints (for HTMX/off-canvas previews) are NOT redefined
here to avoid duplicating full pages — point them at the same DetailView,
just add a second path + a lightweight partial template if you need a true
side-panel later.
"""

from django.urls import path

from catalog.views import views

app_name = "catalog"

urlpatterns = [
    path("", views.CategoryListView.as_view(), name="index"),
    # ── Category ──────────────────────────────────────────────────────────
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category-create"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("categories/<slug:slug>/edit/", views.CategoryUpdateView.as_view(), name="category-update"),
    path("categories/<slug:slug>/delete/", views.CategoryDeleteView.as_view(), name="category-delete"),

    # ── Product ───────────────────────────────────────────────────────────
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product-create"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/<slug:slug>/panel/", views.ProductDetailView.as_view(), name="product-detail-panel"),
    path("products/<slug:slug>/edit/", views.ProductUpdateView.as_view(), name="product-update"),
    path("products/<slug:slug>/delete/", views.ProductDeleteView.as_view(), name="product-delete"),

    # ── Product Comments ──────────────────────────────────────────────────
    path("comments/", views.ProductCommentListView.as_view(), name="comment-list"),
    path("comments/add/", views.ProductCommentCreateView.as_view(), name="comment-create"),
    path("comments/<int:pk>/", views.ProductCommentDetailView.as_view(), name="comment-detail"),
    path("comments/<int:pk>/edit/", views.ProductCommentUpdateView.as_view(), name="comment-update"),
    path("comments/<int:pk>/delete/", views.ProductCommentDeleteView.as_view(), name="comment-delete"),

    # ── Order ─────────────────────────────────────────────────────────────
    path("orders/", views.OrderListView.as_view(), name="order-list"),
    path("orders/add/", views.OrderCreateView.as_view(), name="order-create"),
    path("orders/<str:order_id>/", views.OrderDetailView.as_view(), name="order-detail"),
    path("orders/<str:order_id>/panel/", views.OrderDetailView.as_view(), name="order-detail-panel"),
    path("orders/<str:order_id>/edit/", views.OrderUpdateView.as_view(), name="order-update"),
    path("orders/<str:order_id>/delete/", views.OrderDeleteView.as_view(), name="order-delete"),
    path(
        "orders/<str:order_id>/transition/<str:action>/",
        views.OrderStatusTransitionView.as_view(),
        name="order-transition",
    ),

    # ── Order Items ───────────────────────────────────────────────────────
    path("order-items/", views.OrderItemListView.as_view(), name="orderitem-list"),
    path("order-items/add/", views.OrderItemCreateView.as_view(), name="orderitem-create"),
    path("order-items/<int:pk>/", views.OrderItemDetailView.as_view(), name="orderitem-detail"),
    path("order-items/<int:pk>/edit/", views.OrderItemUpdateView.as_view(), name="orderitem-update"),
    path("order-items/<int:pk>/delete/", views.OrderItemDeleteView.as_view(), name="orderitem-delete"),

    # ── Discount Codes ────────────────────────────────────────────────────
    path("offcodes/", views.OffCodeListView.as_view(), name="offcode-list"),
    path("offcodes/add/", views.OffCodeCreateView.as_view(), name="offcode-create"),
    path("offcodes/<int:pk>/", views.OffCodeDetailView.as_view(), name="offcode-detail"),
    path("offcodes/<int:pk>/edit/", views.OffCodeUpdateView.as_view(), name="offcode-update"),
    path("offcodes/<int:pk>/delete/", views.OffCodeDeleteView.as_view(), name="offcode-delete"),

    # ── Payments ──────────────────────────────────────────────────────────
    # No create URL on purpose: Payments are created by the checkout flow.
    path("payments/", views.PaymentListView.as_view(), name="payment-list"),
    path("payments/<str:payment_id>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    path("payments/<str:payment_id>/panel/", views.PaymentDetailView.as_view(), name="payment-detail-panel"),
    path("payments/<str:payment_id>/edit/", views.PaymentUpdateView.as_view(), name="payment-update"),
    path("payments/<str:payment_id>/delete/", views.PaymentDeleteView.as_view(), name="payment-delete"),

    # ── Specs (single resource, spec_type in the URL) ────────────────────
    path("specs/<str:spec_type>/", views.SpecListView.as_view(), name="spec-list"),
    path("specs/<str:spec_type>/add/", views.SpecCreateView.as_view(), name="spec-create"),
    path("specs/<str:spec_type>/<int:pk>/", views.SpecDetailView.as_view(), name="spec-detail"),
    path("specs/<str:spec_type>/<int:pk>/edit/", views.SpecUpdateView.as_view(), name="spec-update"),
    path("specs/<str:spec_type>/<int:pk>/delete/", views.SpecDeleteView.as_view(), name="spec-delete"),
]
