"""
catalog/forms.py

ModelForms for every model that gets a CRUD interface.

Notes
─────
- Fields marked ``editable=False`` on the model (views, selling_count,
  average_rating, rating_count, slug, order_id, payment_id, usages, etc.)
  are intentionally excluded — they are maintained by the system, not by
  a human filling out a form.
- MoneyField renders as two widgets (amount + currency) automatically via
  django-money's form field, so no special handling is required here.
"""

from django import forms

from catalog.models.catalog import Category, Product, ProductComment
from catalog.models.order import Order, OrderItem
from catalog.models.discount import OffCode
from catalog.models.payment import Payment
from catalog.models.specs import RAM, CPU, GPU, HardDrive, Mouse, Keyboard


def _daisyify(fields):
    """Applies DaisyUI/Tailwind input classes based on widget type."""
    for f in fields.values():
        widget = f.widget
        existing = widget.attrs.get("class", "")
        if isinstance(widget, forms.CheckboxInput):
            css = "checkbox checkbox-primary"
        elif isinstance(widget, forms.Select) or isinstance(widget, forms.SelectMultiple):
            css = "select select-bordered w-full"
        elif isinstance(widget, forms.Textarea):
            css = "textarea textarea-bordered w-full"
        elif isinstance(widget, forms.ClearableFileInput) or isinstance(widget, forms.FileInput):
            css = "file-input file-input-bordered w-full"
        else:
            css = "input input-bordered w-full"
        widget.attrs["class"] = (existing + " " + css).strip()


class BootstrapModelForm(forms.ModelForm):
    """
    Name kept for backwards compatibility with existing subclasses below;
    it now applies DaisyUI/Tailwind classes rather than Bootstrap ones.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _daisyify(self.fields)


# ── Catalog ───────────────────────────────────────────────────────────────────

class CategoryForm(BootstrapModelForm):
    class Meta:
        model = Category
        fields = ["name", "parent"]


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = [
            "name", "description", "user", "category", "image",
            "price", "discount_percentage", "stock", "status",
        ]


class ProductCommentForm(BootstrapModelForm):
    class Meta:
        model = ProductComment
        fields = ["product", "user", "text", "rating"]


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderForm(BootstrapModelForm):
    class Meta:
        model = Order
        fields = [
            "user", "status", "currency", "shipping_address",
            "billing_address", "off_code",
        ]


class OrderItemForm(BootstrapModelForm):
    class Meta:
        model = OrderItem
        fields = ["order", "product", "price_at_order", "quantity"]


# ── Discounts ─────────────────────────────────────────────────────────────────

class OffCodeForm(BootstrapModelForm):
    class Meta:
        model = OffCode
        fields = [
            "code", "description", "starts_at", "ends_at",
            "discount_percent", "fixed_discount_amount",
            "max_discount_per_use", "total_discount_capacity",
            "minimum_order_amount", "usage_limit", "usage_limit_per_user",
            "is_active",
        ]
        widgets = {
            "starts_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned = super().clean()
        percent = cleaned.get("discount_percent")
        fixed = cleaned.get("fixed_discount_amount")
        if percent and fixed:
            raise forms.ValidationError(
                "Choose either a percentage discount OR a fixed amount, not both."
            )
        if not percent and not fixed:
            raise forms.ValidationError(
                "You must set either a percentage discount or a fixed amount."
            )
        return cleaned


# ── Payments ──────────────────────────────────────────────────────────────────

class PaymentForm(BootstrapModelForm):
    class Meta:
        model = Payment
        fields = [
            "order", "description", "status", "amount", "value_added_tax",
            "payment_method", "transaction_id", "authority", "user_ip_address",
        ]


# ── Specs ─────────────────────────────────────────────────────────────────────

class RAMForm(BootstrapModelForm):
    class Meta:
        model = RAM
        fields = ["product", "capacity_gb", "speed_mhz", "ddr_type"]


class CPUForm(BootstrapModelForm):
    class Meta:
        model = CPU
        fields = [
            "product", "cores", "threads", "base_clock", "boost_clock",
            "socket", "tdp_watts",
        ]


class GPUForm(BootstrapModelForm):
    class Meta:
        model = GPU
        fields = [
            "product", "memory_gb", "memory_type", "core_clock_mhz",
            "boost_clock_mhz", "tdp_watts",
        ]


class HardDriveForm(BootstrapModelForm):
    class Meta:
        model = HardDrive
        fields = [
            "product", "capacity_gb", "drive_type", "form_factor",
            "interface", "read_speed_mb_s", "write_speed_mb_s",
        ]


class MouseForm(BootstrapModelForm):
    class Meta:
        model = Mouse
        fields = [
            "product", "dpi", "connection_type", "is_gaming", "has_rgb",
            "buttons_count", "weight_grams",
        ]


class KeyboardForm(BootstrapModelForm):
    class Meta:
        model = Keyboard
        fields = [
            "product", "is_gaming", "layout", "switch_type", "has_rgb",
            "has_num_pad", "is_wireless",
        ]
