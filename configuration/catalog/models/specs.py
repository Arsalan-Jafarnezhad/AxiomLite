"""
shop/models/specs.py

Hardware specification models (1-to-1 extensions of Product).

Uses ``TimeStampedModel`` from django-model-utils for ``created`` / ``modified``
timestamps without a custom abstract base.
"""

from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils.models import TimeStampedModel


class RAM(TimeStampedModel):
    product     = models.OneToOneField("catalog.Product", on_delete=models.CASCADE, related_name="ram_specs")
    capacity_gb = models.PositiveIntegerField(help_text=_("Capacity in GB."))
    speed_mhz   = models.PositiveIntegerField(help_text=_("Speed in MHz."))
    ddr_type    = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("DDR generation (e.g. 4 for DDR4, 5 for DDR5)."),
    )

    class Meta:
        verbose_name = _("RAM Spec")

    def __str__(self) -> str:
        return f"{self.capacity_gb} GB DDR{self.ddr_type} @ {self.speed_mhz} MHz"


class CPU(TimeStampedModel):
    product     = models.OneToOneField("catalog.Product", on_delete=models.CASCADE, related_name="cpu_specs")
    cores       = models.PositiveIntegerField()
    threads     = models.PositiveIntegerField()
    base_clock  = models.DecimalField(max_digits=4, decimal_places=2, help_text=_("Base clock in GHz."))
    boost_clock = models.DecimalField(max_digits=4, decimal_places=2, help_text=_("Boost clock in GHz."))
    socket      = models.CharField(max_length=50, help_text=_("e.g. AM5, LGA1851."))
    tdp_watts   = models.PositiveIntegerField(null=True, blank=True, help_text=_("Thermal design power in watts."))

    class Meta:
        verbose_name = _("CPU Spec")

    def __str__(self) -> str:
        return f"{self.cores}C/{self.threads}T — {self.boost_clock} GHz ({self.socket})"


class GPU(TimeStampedModel):
    product        = models.OneToOneField("catalog.Product", on_delete=models.CASCADE, related_name="gpu_specs")
    memory_gb      = models.PositiveIntegerField(help_text=_("VRAM in GB."))
    memory_type    = models.CharField(max_length=20, help_text=_("e.g. GDDR7, GDDR6X."))
    core_clock_mhz = models.PositiveIntegerField(help_text=_("Base core clock in MHz."))
    boost_clock_mhz = models.PositiveIntegerField(null=True, blank=True, help_text=_("Boost clock in MHz."))
    tdp_watts       = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _("GPU Spec")

    def __str__(self) -> str:
        return f"{self.memory_gb} GB {self.memory_type}"


class HardDrive(TimeStampedModel):

    class DriveType(models.IntegerChoices):
        HDD  = 0, "HDD"
        SSD  = 1, "SSD"
        NVME = 2, "NVMe"

    product          = models.OneToOneField("catalog.Product", on_delete=models.CASCADE, related_name="hard_specs")
    capacity_gb      = models.PositiveIntegerField()
    drive_type       = models.IntegerField(choices=DriveType.choices)
    form_factor      = models.CharField(max_length=20, blank=True, help_text=_('e.g. 2.5", 3.5", M.2'))
    interface        = models.CharField(max_length=30, blank=True, help_text=_("e.g. SATA III, PCIe 4.0 x4."))
    read_speed_mb_s  = models.PositiveIntegerField(null=True, blank=True, help_text=_("Sequential read MB/s."))
    write_speed_mb_s = models.PositiveIntegerField(null=True, blank=True, help_text=_("Sequential write MB/s."))

    class Meta:
        verbose_name = _("Hard Drive Spec")

    def __str__(self) -> str:
        return f"{self.capacity_gb} GB {self.get_drive_type_display()}"


class Mouse(TimeStampedModel):

    class ConnectionType(models.IntegerChoices):
        WIRED    = 0, "Wired"
        WIRELESS = 1, "Wireless"
        BOTH     = 2, "Wired / Wireless"

    product         = models.OneToOneField("catalog.Product", on_delete=models.CASCADE, related_name="mouse_specs")
    dpi             = models.PositiveIntegerField(null=True, blank=True, help_text=_("Max DPI."))
    connection_type = models.IntegerField(choices=ConnectionType.choices)
    is_gaming       = models.BooleanField(default=False)
    has_rgb         = models.BooleanField(default=False)
    buttons_count   = models.PositiveIntegerField(null=True, blank=True)
    weight_grams    = models.PositiveIntegerField(null=True, blank=True, help_text=_("Weight in grams."))

    class Meta:
        verbose_name = _("Mouse Spec")

    def __str__(self) -> str:
        tag = "Gaming" if self.is_gaming else "Office"
        return f"{tag} Mouse — {self.product.name}"


class Keyboard(TimeStampedModel):

    class Layout(models.TextChoices):
        FULL        = "FULL", _("Full-size")
        TKL         = "TKL",  _("Tenkeyless")
        SIXTY       = "60",   _("60%")
        SEVENTYFIVE = "75",   _("75%")
        SIXTY_FIVE  = "65",   _("65%")

    class SwitchType(models.TextChoices):
        MECHANICAL = "MECHANICAL", _("Mechanical")
        MEMBRANE   = "MEMBRANE",   _("Membrane")
        OPTICAL    = "OPTICAL",    _("Optical")
        HALL_EFFECT = "HALL",      _("Hall Effect")

    product     = models.OneToOneField("catalog.Product", on_delete=models.CASCADE, related_name="keyboard_specs")
    is_gaming   = models.BooleanField(default=False)
    layout      = models.CharField(max_length=10, choices=Layout.choices, blank=True)
    switch_type = models.CharField(max_length=20, choices=SwitchType.choices, blank=True)
    has_rgb     = models.BooleanField(default=False)
    has_num_pad = models.BooleanField(default=True)
    is_wireless = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Keyboard Spec")

    def __str__(self) -> str:
        return f"{self.get_layout_display()} {self.get_switch_type_display()} Keyboard"
