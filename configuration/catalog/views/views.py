"""
catalog/views.py

Class-based CRUD views for:
    Category, Product, ProductComment          (catalog/models/catalog.py)
    Order, OrderItem                            (catalog/models/order.py)
    OffCode                                      (catalog/models/discount.py)
    Payment                                      (catalog/models/payment.py)
    RAM, CPU, GPU, HardDrive, Mouse, Keyboard    (shop/models/specs.py)

Design choices
──────────────
- Standard ListView / DetailView / CreateView / UpdateView / DeleteView
  per model, all sharing a small set of generic templates
  (``catalog/generic_list.html``, ``generic_form.html``,
  ``generic_detail.html``, ``generic_confirm_delete.html``) driven by
  each view's ``model_label`` / ``list_url`` context so we don't hand-write
  a template per model.
- ``SoftDeletableModel`` models (Product, ProductComment, Order, OffCode,
  Payment) are "deleted" via their ``is_removed`` flag rather than a hard
  DB delete — the delete views call ``.delete()`` which model-utils routes
  to a soft delete automatically, and list views use the model's default
  manager (already filtered to non-removed rows).
- Payment intentionally has no CreateView exposed in urls.py — payments
  should be created by the checkout flow, not an admin form — but the
  view class is still provided in case a staff "manual payment" screen is
  wanted later.
- Order status changes go through ``mark_as_*`` methods (business rules
  enforced there), exposed as simple POST-only views rather than editing
  ``status`` directly in the UpdateView.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View,
)

from catalog.models.catalog import Category, Product, ProductComment
from catalog.models.order import Order, OrderItem
from catalog.models.discount import OffCode
from catalog.models.payment import Payment
from catalog.models.specs import RAM, CPU, GPU, HardDrive, Mouse, Keyboard

from catalog.forms import (
    CategoryForm, ProductForm, ProductCommentForm,
    OrderForm, OrderItemForm,
    OffCodeForm,
    PaymentForm,
    RAMForm, CPUForm, GPUForm, HardDriveForm, MouseForm, KeyboardForm,
)


# ── Generic mixins ─────────────────────────────────────────────────────────────

class GenericCRUDMixin:
    """
    Supplies the extra context every generic template needs:
    ``model_label`` (display name), ``list_url_name`` (for "back to list"
    and post-save/delete redirects) and ``verbose_name_plural``.

    ``lookup_kwarg`` tells the templates which URL kwarg identifies a single
    object for this model (``pk`` by default; ``slug`` for Category/Product,
    ``order_id`` for Order, ``payment_id`` for Payment) so generic templates
    can build detail/edit/delete links without hardcoding per model.
    """
    model_label: str = ""
    list_url_name: str = ""
    create_url_name: str = ""
    detail_url_name: str = ""
    update_url_name: str = ""
    delete_url_name: str = ""
    lookup_kwarg: str = "pk"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_label"] = self.model_label or self.model._meta.verbose_name
        ctx["model_label_plural"] = self.model._meta.verbose_name_plural
        ctx["list_url_name"] = self.list_url_name
        ctx["create_url_name"] = self.create_url_name
        ctx["detail_url_name"] = self.detail_url_name
        ctx["update_url_name"] = self.update_url_name
        ctx["delete_url_name"] = self.delete_url_name
        ctx["lookup_kwarg"] = self.lookup_kwarg
        return ctx

    def get_success_url(self):
        return reverse_lazy(self.list_url_name)


class GenericListView(GenericCRUDMixin, ListView):
    template_name = "catalog/generic_list.html"
    paginate_by = 25
    context_object_name = "object_list"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lookup = self.lookup_kwarg
        rows = []
        for obj in ctx["object_list"]:
            lookup_value = getattr(obj, lookup)
            rows.append({
                "obj": obj,
                "detail_url": reverse_lazy(self.detail_url_name, kwargs={lookup: lookup_value}),
                "update_url": reverse_lazy(self.update_url_name, kwargs={lookup: lookup_value}),
                "delete_url": reverse_lazy(self.delete_url_name, kwargs={lookup: lookup_value}),
            })
        ctx["rows"] = rows
        return ctx


class GenericDetailView(GenericCRUDMixin, DetailView):
    template_name = "catalog/generic_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        lookup = self.lookup_kwarg
        lookup_value = getattr(self.object, lookup)
        if self.update_url_name:
            ctx["update_url"] = reverse_lazy(self.update_url_name, kwargs={lookup: lookup_value})
        if self.delete_url_name:
            ctx["delete_url"] = reverse_lazy(self.delete_url_name, kwargs={lookup: lookup_value})
        return ctx


class GenericCreateView(GenericCRUDMixin, CreateView):
    template_name = "catalog/generic_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"{self.model_label} created successfully.")
        return response


class GenericUpdateView(GenericCRUDMixin, UpdateView):
    template_name = "catalog/generic_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"{self.model_label} updated successfully.")
        return response


class GenericDeleteView(GenericCRUDMixin, DeleteView):
    template_name = "catalog/generic_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, f"{self.model_label} deleted successfully.")
        return super().form_valid(form)


# ── Category ────────────────────────────────────────────────────────────────

class CategoryListView(GenericListView):
    model = Category
    model_label = "Category"
    list_url_name = "catalog:category-list"
    create_url_name = "catalog:category-create"
    detail_url_name = "catalog:category-detail"
    update_url_name = "catalog:category-update"
    delete_url_name = "catalog:category-delete"
    lookup_kwarg = "slug"
    ordering = ["name"]


class CategoryDetailView(GenericDetailView):
    model = Category
    model_label = "Category"
    list_url_name = "catalog:category-list"
    create_url_name = "catalog:category-create"
    detail_url_name = "catalog:category-detail"
    update_url_name = "catalog:category-update"
    delete_url_name = "catalog:category-delete"
    lookup_kwarg = "slug"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["products"] = self.object.products.all()[:50]
        return ctx


class CategoryCreateView(GenericCreateView):
    model = Category
    form_class = CategoryForm
    model_label = "Category"
    list_url_name = "catalog:category-list"
    create_url_name = "catalog:category-create"
    detail_url_name = "catalog:category-detail"
    update_url_name = "catalog:category-update"
    delete_url_name = "catalog:category-delete"
    lookup_kwarg = "slug"


class CategoryUpdateView(GenericUpdateView):
    model = Category
    form_class = CategoryForm
    model_label = "Category"
    list_url_name = "catalog:category-list"
    create_url_name = "catalog:category-create"
    detail_url_name = "catalog:category-detail"
    update_url_name = "catalog:category-update"
    delete_url_name = "catalog:category-delete"
    lookup_kwarg = "slug"


class CategoryDeleteView(GenericDeleteView):
    model = Category
    model_label = "Category"
    list_url_name = "catalog:category-list"
    create_url_name = "catalog:category-create"
    detail_url_name = "catalog:category-detail"
    update_url_name = "catalog:category-update"
    delete_url_name = "catalog:category-delete"
    lookup_kwarg = "slug"


# ── Product ─────────────────────────────────────────────────────────────────

class ProductListView(GenericListView):
    model = Product
    model_label = "Product"
    list_url_name = "catalog:product-list"
    create_url_name = "catalog:product-create"
    detail_url_name = "catalog:product-detail"
    update_url_name = "catalog:product-update"
    delete_url_name = "catalog:product-delete"
    lookup_kwarg = "slug"

    def get_queryset(self):
        qs = super().get_queryset().select_related("category", "user")
        q = self.request.GET.get("q")
        status = self.request.GET.get("status")
        if q:
            qs = qs.filter(name__icontains=q)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Product.Status.choices
        ctx["q"] = self.request.GET.get("q", "")
        ctx["status"] = self.request.GET.get("status", "")
        return ctx


class ProductDetailView(GenericDetailView):
    model = Product
    model_label = "Product"
    list_url_name = "catalog:product-list"
    create_url_name = "catalog:product-create"
    detail_url_name = "catalog:product-detail"
    update_url_name = "catalog:product-update"
    delete_url_name = "catalog:product-delete"
    lookup_kwarg = "slug"
    template_name = "catalog/product_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["comments"] = self.object.comments.select_related("user").all()[:50]
        return ctx


class ProductCreateView(GenericCreateView):
    model = Product
    form_class = ProductForm
    model_label = "Product"
    list_url_name = "catalog:product-list"
    create_url_name = "catalog:product-create"
    detail_url_name = "catalog:product-detail"
    update_url_name = "catalog:product-update"
    delete_url_name = "catalog:product-delete"
    lookup_kwarg = "slug"


class ProductUpdateView(GenericUpdateView):
    model = Product
    form_class = ProductForm
    model_label = "Product"
    list_url_name = "catalog:product-list"
    create_url_name = "catalog:product-create"
    detail_url_name = "catalog:product-detail"
    update_url_name = "catalog:product-update"
    delete_url_name = "catalog:product-delete"
    lookup_kwarg = "slug"


class ProductDeleteView(GenericDeleteView):
    model = Product
    model_label = "Product"
    list_url_name = "catalog:product-list"
    create_url_name = "catalog:product-create"
    detail_url_name = "catalog:product-detail"
    update_url_name = "catalog:product-update"
    delete_url_name = "catalog:product-delete"
    lookup_kwarg = "slug"


# ── ProductComment ────────────────────────────────────────────────────────────

class ProductCommentListView(GenericListView):
    model = ProductComment
    model_label = "Product Comment"
    list_url_name = "catalog:comment-list"
    create_url_name = "catalog:comment-create"
    detail_url_name = "catalog:comment-detail"
    update_url_name = "catalog:comment-update"
    delete_url_name = "catalog:comment-delete"
    lookup_kwarg = "pk"

    def get_queryset(self):
        qs = super().get_queryset().select_related("product", "user")
        product_id = self.request.GET.get("product")
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs


class ProductCommentDetailView(GenericDetailView):
    model = ProductComment
    model_label = "Product Comment"
    list_url_name = "catalog:comment-list"
    create_url_name = "catalog:comment-create"
    detail_url_name = "catalog:comment-detail"
    update_url_name = "catalog:comment-update"
    delete_url_name = "catalog:comment-delete"
    lookup_kwarg = "pk"


class ProductCommentCreateView(GenericCreateView):
    model = ProductComment
    form_class = ProductCommentForm
    model_label = "Product Comment"
    list_url_name = "catalog:comment-list"
    create_url_name = "catalog:comment-create"
    detail_url_name = "catalog:comment-detail"
    update_url_name = "catalog:comment-update"
    delete_url_name = "catalog:comment-delete"
    lookup_kwarg = "pk"


class ProductCommentUpdateView(GenericUpdateView):
    model = ProductComment
    form_class = ProductCommentForm
    model_label = "Product Comment"
    list_url_name = "catalog:comment-list"
    create_url_name = "catalog:comment-create"
    detail_url_name = "catalog:comment-detail"
    update_url_name = "catalog:comment-update"
    delete_url_name = "catalog:comment-delete"
    lookup_kwarg = "pk"


class ProductCommentDeleteView(GenericDeleteView):
    model = ProductComment
    model_label = "Product Comment"
    list_url_name = "catalog:comment-list"
    create_url_name = "catalog:comment-create"
    detail_url_name = "catalog:comment-detail"
    update_url_name = "catalog:comment-update"
    delete_url_name = "catalog:comment-delete"
    lookup_kwarg = "pk"


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderListView(GenericListView):
    model = Order
    model_label = "Order"
    list_url_name = "catalog:order-list"
    create_url_name = "catalog:order-create"
    detail_url_name = "catalog:order-detail"
    update_url_name = "catalog:order-update"
    delete_url_name = "catalog:order-delete"
    lookup_kwarg = "order_id"

    def get_queryset(self):
        qs = super().get_queryset().select_related("user", "off_code")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Order.Status.choices
        ctx["status"] = self.request.GET.get("status", "")
        return ctx


class OrderDetailView(GenericDetailView):
    model = Order
    model_label = "Order"
    list_url_name = "catalog:order-list"
    create_url_name = "catalog:order-create"
    detail_url_name = "catalog:order-detail"
    update_url_name = "catalog:order-update"
    delete_url_name = "catalog:order-delete"
    lookup_kwarg = "order_id"
    slug_field = "order_id"
    slug_url_kwarg = "order_id"
    template_name = "catalog/order_detail.html"

    # Which "mark as ..." buttons make sense from the order's current status.
    NEXT_TRANSITIONS = {
        Order.Status.PENDING_PAYMENT: [("paid", "Paid"), ("cancelled", "Cancelled")],
        Order.Status.PAID: [("processing", "Processing"), ("shipped", "Shipped"), ("cancelled", "Cancelled")],
        Order.Status.PROCESSING: [("shipped", "Shipped"), ("cancelled", "Cancelled")],
        Order.Status.SHIPPED: [("delivered", "Delivered"), ("refunded", "Refunded")],
        Order.Status.DELIVERED: [("refunded", "Refunded")],
        Order.Status.CANCELLED: [],
        Order.Status.REFUNDED: [],
    }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["items"] = self.object.get_items_detail()
        ctx["payment"] = getattr(self.object, "payment", None)
        ctx["transitions"] = self.NEXT_TRANSITIONS.get(self.object.status, [])
        return ctx


class OrderCreateView(GenericCreateView):
    model = Order
    form_class = OrderForm
    model_label = "Order"
    list_url_name = "catalog:order-list"
    create_url_name = "catalog:order-create"
    detail_url_name = "catalog:order-detail"
    update_url_name = "catalog:order-update"
    delete_url_name = "catalog:order-delete"
    lookup_kwarg = "order_id"


class OrderUpdateView(GenericUpdateView):
    model = Order
    form_class = OrderForm
    model_label = "Order"
    list_url_name = "catalog:order-list"
    create_url_name = "catalog:order-create"
    detail_url_name = "catalog:order-detail"
    update_url_name = "catalog:order-update"
    delete_url_name = "catalog:order-delete"
    lookup_kwarg = "order_id"
    slug_field = "order_id"
    slug_url_kwarg = "order_id"


class OrderDeleteView(GenericDeleteView):
    model = Order
    model_label = "Order"
    list_url_name = "catalog:order-list"
    create_url_name = "catalog:order-create"
    detail_url_name = "catalog:order-detail"
    update_url_name = "catalog:order-update"
    delete_url_name = "catalog:order-delete"
    lookup_kwarg = "order_id"
    slug_field = "order_id"
    slug_url_kwarg = "order_id"


class OrderStatusTransitionView(LoginRequiredMixin, View):
    """
    POST-only endpoint that drives Order's ``mark_as_*`` methods so status
    transitions always go through the model's guarded business rules
    instead of being set directly via the UpdateView form.

    URL: /orders/<order_id>/transition/<action>/
    action ∈ paid|processing|shipped|delivered|cancelled|refunded
    """

    TRANSITIONS = {
        "paid": "mark_as_paid",
        "processing": "mark_as_processing",
        "shipped": "mark_as_shipped",
        "delivered": "mark_as_delivered",
        "cancelled": "mark_as_cancelled",
        "refunded": "mark_as_refunded",
    }

    def post(self, request, order_id, action):
        order = get_object_or_404(Order, order_id=order_id)
        method_name = self.TRANSITIONS.get(action)
        if not method_name:
            messages.error(request, f"Unknown transition '{action}'.")
        else:
            ok = getattr(order, method_name)()
            if ok:
                messages.success(request, f"Order moved to '{action}'.")
            else:
                messages.error(
                    request,
                    f"Cannot transition order from '{order.get_status_display()}' to '{action}'.",
                )
        return redirect("catalog:order-detail", order_id=order_id)


# ── OrderItem ─────────────────────────────────────────────────────────────────

class OrderItemListView(GenericListView):
    model = OrderItem
    model_label = "Order Item"
    list_url_name = "catalog:orderitem-list"
    create_url_name = "catalog:orderitem-create"
    detail_url_name = "catalog:orderitem-detail"
    update_url_name = "catalog:orderitem-update"
    delete_url_name = "catalog:orderitem-delete"
    lookup_kwarg = "pk"

    def get_queryset(self):
        qs = super().get_queryset().select_related("order", "product")
        order_id = self.request.GET.get("order")
        if order_id:
            qs = qs.filter(order_id=order_id)
        return qs


class OrderItemDetailView(GenericDetailView):
    model = OrderItem
    model_label = "Order Item"
    list_url_name = "catalog:orderitem-list"
    create_url_name = "catalog:orderitem-create"
    detail_url_name = "catalog:orderitem-detail"
    update_url_name = "catalog:orderitem-update"
    delete_url_name = "catalog:orderitem-delete"
    lookup_kwarg = "pk"


class OrderItemCreateView(GenericCreateView):
    model = OrderItem
    form_class = OrderItemForm
    model_label = "Order Item"
    list_url_name = "catalog:orderitem-list"
    create_url_name = "catalog:orderitem-create"
    detail_url_name = "catalog:orderitem-detail"
    update_url_name = "catalog:orderitem-update"
    delete_url_name = "catalog:orderitem-delete"
    lookup_kwarg = "pk"

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.order.recalculate_amounts()
        self.object.order.save()
        return response


class OrderItemUpdateView(GenericUpdateView):
    model = OrderItem
    form_class = OrderItemForm
    model_label = "Order Item"
    list_url_name = "catalog:orderitem-list"
    create_url_name = "catalog:orderitem-create"
    detail_url_name = "catalog:orderitem-detail"
    update_url_name = "catalog:orderitem-update"
    delete_url_name = "catalog:orderitem-delete"
    lookup_kwarg = "pk"

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.order.recalculate_amounts()
        self.object.order.save()
        return response


class OrderItemDeleteView(GenericDeleteView):
    model = OrderItem
    model_label = "Order Item"
    list_url_name = "catalog:orderitem-list"
    create_url_name = "catalog:orderitem-create"
    detail_url_name = "catalog:orderitem-detail"
    update_url_name = "catalog:orderitem-update"
    delete_url_name = "catalog:orderitem-delete"
    lookup_kwarg = "pk"

    @transaction.atomic
    def form_valid(self, form):
        order = self.get_object().order
        response = super().form_valid(form)
        order.recalculate_amounts()
        order.save()
        return response


# ── OffCode (discount) ────────────────────────────────────────────────────────

class OffCodeListView(GenericListView):
    model = OffCode
    model_label = "Discount Code"
    list_url_name = "catalog:offcode-list"
    create_url_name = "catalog:offcode-create"
    detail_url_name = "catalog:offcode-detail"
    update_url_name = "catalog:offcode-update"
    delete_url_name = "catalog:offcode-delete"
    lookup_kwarg = "pk"


class OffCodeDetailView(GenericDetailView):
    model = OffCode
    model_label = "Discount Code"
    list_url_name = "catalog:offcode-list"
    create_url_name = "catalog:offcode-create"
    detail_url_name = "catalog:offcode-detail"
    update_url_name = "catalog:offcode-update"
    delete_url_name = "catalog:offcode-delete"
    lookup_kwarg = "pk"


class OffCodeCreateView(GenericCreateView):
    model = OffCode
    form_class = OffCodeForm
    model_label = "Discount Code"
    list_url_name = "catalog:offcode-list"
    create_url_name = "catalog:offcode-create"
    detail_url_name = "catalog:offcode-detail"
    update_url_name = "catalog:offcode-update"
    delete_url_name = "catalog:offcode-delete"
    lookup_kwarg = "pk"


class OffCodeUpdateView(GenericUpdateView):
    model = OffCode
    form_class = OffCodeForm
    model_label = "Discount Code"
    list_url_name = "catalog:offcode-list"
    create_url_name = "catalog:offcode-create"
    detail_url_name = "catalog:offcode-detail"
    update_url_name = "catalog:offcode-update"
    delete_url_name = "catalog:offcode-delete"
    lookup_kwarg = "pk"


class OffCodeDeleteView(GenericDeleteView):
    model = OffCode
    model_label = "Discount Code"
    list_url_name = "catalog:offcode-list"
    create_url_name = "catalog:offcode-create"
    detail_url_name = "catalog:offcode-detail"
    update_url_name = "catalog:offcode-update"
    delete_url_name = "catalog:offcode-delete"
    lookup_kwarg = "pk"


# ── Payment ───────────────────────────────────────────────────────────────────
# Payments are primarily read-only from the admin UI; creation happens via
# the checkout flow. Update is limited to reconciliation fields (status,
# transaction_id) — still routed through PaymentForm for simplicity here.

class PaymentListView(GenericListView):
    model = Payment
    model_label = "Payment"
    list_url_name = "catalog:payment-list"
    create_url_name = "catalog:payment-create"
    detail_url_name = "catalog:payment-detail"
    update_url_name = "catalog:payment-update"
    delete_url_name = "catalog:payment-delete"
    lookup_kwarg = "payment_id"

    def get_queryset(self):
        qs = super().get_queryset().select_related("order")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_choices"] = Payment.Status.choices
        ctx["status"] = self.request.GET.get("status", "")
        return ctx


class PaymentDetailView(GenericDetailView):
    model = Payment
    model_label = "Payment"
    list_url_name = "catalog:payment-list"
    create_url_name = "catalog:payment-create"
    detail_url_name = "catalog:payment-detail"
    update_url_name = "catalog:payment-update"
    delete_url_name = "catalog:payment-delete"
    lookup_kwarg = "payment_id"
    slug_field = "payment_id"
    slug_url_kwarg = "payment_id"


class PaymentUpdateView(GenericUpdateView):
    model = Payment
    form_class = PaymentForm
    model_label = "Payment"
    list_url_name = "catalog:payment-list"
    create_url_name = "catalog:payment-create"
    detail_url_name = "catalog:payment-detail"
    update_url_name = "catalog:payment-update"
    delete_url_name = "catalog:payment-delete"
    lookup_kwarg = "payment_id"
    slug_field = "payment_id"
    slug_url_kwarg = "payment_id"


class PaymentDeleteView(GenericDeleteView):
    model = Payment
    model_label = "Payment"
    list_url_name = "catalog:payment-list"
    create_url_name = "catalog:payment-create"
    detail_url_name = "catalog:payment-detail"
    update_url_name = "catalog:payment-update"
    delete_url_name = "catalog:payment-delete"
    lookup_kwarg = "payment_id"
    slug_field = "payment_id"
    slug_url_kwarg = "payment_id"


# ── Specs (RAM / CPU / GPU / HardDrive / Mouse / Keyboard) ────────────────────
# Instead of six separate models with six separate URL sets, specs are
# treated as ONE "spec" resource with a ``spec_type`` URL segment
# (/specs/<spec_type>/...). A registry maps each spec_type slug to its
# model, form, display label and a Material Symbols icon name used in the
# UI. Add a new spec type by adding one line to SPEC_REGISTRY — no new
# views or URLs required.

SPEC_REGISTRY = {
    "ram":       {"model": RAM,       "form": RAMForm,       "label": "RAM",        "icon": "memory"},
    "cpu":       {"model": CPU,       "form": CPUForm,       "label": "CPU",        "icon": "developer_board"},
    "gpu":       {"model": GPU,       "form": GPUForm,       "label": "GPU",        "icon": "videogame_asset"},
    "harddrive": {"model": HardDrive, "form": HardDriveForm, "label": "Hard Drive", "icon": "hard_drive"},
    "mouse":     {"model": Mouse,     "form": MouseForm,     "label": "Mouse",      "icon": "mouse"},
    "keyboard":  {"model": Keyboard,  "form": KeyboardForm,  "label": "Keyboard",   "icon": "keyboard"},
}


class SpecTypeMixin:
    """Resolves ``self.kwargs['spec_type']`` into a model/form/label via
    SPEC_REGISTRY and makes them available as ``self.model`` etc."""

    def dispatch(self, request, *args, **kwargs):
        spec_type = kwargs.get("spec_type")
        entry = SPEC_REGISTRY.get(spec_type)
        if entry is None:
            from django.http import Http404
            raise Http404(f"Unknown spec type '{spec_type}'.")
        self.spec_type = spec_type
        self.model = entry["model"]
        self.form_class = entry["form"]
        self.model_label = entry["label"]
        self.spec_icon = entry["icon"]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["spec_type"] = self.spec_type
        ctx["spec_icon"] = self.spec_icon
        ctx["spec_registry"] = SPEC_REGISTRY
        return ctx


class SpecListView(SpecTypeMixin, ListView):
    template_name = "catalog/spec_list.html"
    paginate_by = 25
    context_object_name = "object_list"

    def get_queryset(self):
        return self.model.objects.select_related("product").all()


class SpecDetailView(SpecTypeMixin, DetailView):
    template_name = "catalog/generic_detail.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_label"] = self.model_label
        ctx["list_url"] = reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})
        ctx["update_url"] = reverse_lazy(
            "catalog:spec-update", kwargs={"spec_type": self.spec_type, "pk": self.object.pk}
        )
        ctx["delete_url"] = reverse_lazy(
            "catalog:spec-delete", kwargs={"spec_type": self.spec_type, "pk": self.object.pk}
        )
        return ctx


class SpecCreateView(SpecTypeMixin, CreateView):
    template_name = "catalog/generic_form.html"

    def get_success_url(self):
        messages.success(self.request, f"{self.model_label} spec created successfully.")
        return reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_label"] = f"{self.model_label} Spec"
        ctx["list_url"] = reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})
        return ctx


class SpecUpdateView(SpecTypeMixin, UpdateView):
    template_name = "catalog/generic_form.html"

    def get_success_url(self):
        messages.success(self.request, f"{self.model_label} spec updated successfully.")
        return reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_label"] = f"{self.model_label} Spec"
        ctx["list_url"] = reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})
        return ctx


class SpecDeleteView(SpecTypeMixin, DeleteView):
    template_name = "catalog/generic_confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, f"{self.model_label} spec deleted successfully.")
        return reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["model_label"] = f"{self.model_label} Spec"
        ctx["list_url_name"] = None  # list_url below is fully resolved instead
        ctx["list_url"] = reverse_lazy("catalog:spec-list", kwargs={"spec_type": self.spec_type})
        return ctx
