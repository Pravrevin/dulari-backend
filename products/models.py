from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, max_length=255)
    count_of_products = models.IntegerField(default=0)

    class Meta:
        db_table = "products_category"
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=255)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    is_discontinued = models.BooleanField(default=False)
    manufacturer_name = models.CharField(max_length=255)
    pack_size_label = models.CharField(max_length=255)
    short_composition1 = models.CharField(max_length=500, blank=True, default="")
    short_composition2 = models.CharField(max_length=500, blank=True, default="")

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Flag attributes for filtering
    is_new_launch = models.BooleanField(default=False, help_text="Mark product as a New Launch")
    is_trending_near_you = models.BooleanField(default=False, help_text="Mark product as Trending Near You")
    is_in_spotlight = models.BooleanField(default=False, help_text="Mark product as In the Spotlight")
    is_approved = models.BooleanField(default=False, help_text="Approved by a super admin from the admin panel")

    class Meta:
        db_table = "products_product"
        ordering = ["product_id"]

    def __str__(self):
        return self.product_name


class DealOfTheDay(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="deals",
    )
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Discount percentage e.g. 20.00 for 20%")
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price after applying discount")
    offer_ends_at = models.DateTimeField(help_text="Date and time when the offer expires")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_dealoftheday"
        ordering = ["offer_ends_at"]

    def __str__(self):
        return f"{self.product.product_name} — {self.discount_percentage}% off"

    def save(self, *args, **kwargs):
        # Auto-calculate discounted price from product MRP if not explicitly set
        if not self.discounted_price and self.product_id:
            mrp = self.product.mrp
            self.discounted_price = round(mrp - (mrp * self.discount_percentage / 100), 2)
        super().save(*args, **kwargs)


class SuperSavingDeal(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="super_saving_deal",
    )
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Discount percentage e.g. 30.00 for 30%"
    )
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Price after applying the discount"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_supersavingdeal"
        ordering = ["-discount_percentage"]

    def __str__(self):
        return f"{self.product.product_name} — {self.discount_percentage}% off (Super Saving)"

    def save(self, *args, **kwargs):
        if not self.discounted_price and self.product_id:
            mrp = self.product.mrp
            self.discounted_price = round(mrp - (mrp * self.discount_percentage / 100), 2)
        super().save(*args, **kwargs)


class Combo(models.Model):
    combo_name = models.CharField(max_length=255)
    product1 = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="combos_as_product1",
    )
    product2 = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="combos_as_product2",
    )
    tags = models.JSONField(
        default=list,
        help_text="List of tag strings e.g. ['pain_relief', 'fever']",
    )
    combo_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products_combo"
        ordering = ["combo_name"]

    def __str__(self):
        return self.combo_name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "products_productimage"

    def __str__(self):
        return f"Image for {self.product.product_name}"


class GenericMedicine(models.Model):
    generic_product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, help_text="Generic drug name e.g. Amoxycillin 500mg Tablet")
    brand = models.CharField(max_length=255, help_text="Generic manufacturer brand name")
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Discount % compared to the linked branded product MRP. "
                  "Formula: ((product.mrp - generic.mrp) / product.mrp) * 100",
    )
    image = models.ImageField(upload_to="generic_medicines/", blank=True, null=True, max_length=255)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="generic_medicines",
    )

    class Meta:
        db_table = "products_genericmedicine"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.brand})"


class ProductFeature(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="feature",
        primary_key=True,
    )
    description = models.TextField(blank=True, default="", help_text="Product description")
    uses = models.TextField(blank=True, default="", help_text="Semicolon-separated list of uses")
    benefits = models.TextField(blank=True, default="", help_text="Semicolon-separated list of benefits")
    side_effects = models.TextField(blank=True, default="", help_text="Semicolon-separated list of side effects")
    how_to_use = models.TextField(blank=True, default="", help_text="Instructions on how to use the product")
    substitutes = models.TextField(blank=True, default="", help_text="Semicolon-separated list of substitute products")

    class Meta:
        db_table = "products_productfeature"

    def __str__(self):
        return f"Features for {self.product.product_name}"
