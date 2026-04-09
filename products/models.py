from django.db import models


class Product(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=255)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    is_discontinued = models.BooleanField(default=False)
    manufacturer_name = models.CharField(max_length=255)
    pack_size_label = models.CharField(max_length=255)
    short_composition1 = models.CharField(max_length=500, blank=True, default="")
    short_composition2 = models.CharField(max_length=500, blank=True, default="")

    # Flag attributes for filtering
    is_new_launch = models.BooleanField(default=False, help_text="Mark product as a New Launch")
    is_trending_near_you = models.BooleanField(default=False, help_text="Mark product as Trending Near You")
    is_in_spotlight = models.BooleanField(default=False, help_text="Mark product as In the Spotlight")

    class Meta:
        db_table = "products_product"
        ordering = ["product_id"]

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "products_productimage"

    def __str__(self):
        return f"Image for {self.product.product_name}"
