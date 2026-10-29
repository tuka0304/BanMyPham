from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Extending AbstractUser covers username, email, password
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, default='CUSTOMER') # ADMIN, EMPLOYEE, or CUSTOMER
    
    class Meta:
        db_table = 'users'
        
    def is_admin(self):
        return self.role == 'ADMIN'

    def is_employee(self):
        return self.role == 'EMPLOYEE'

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    class Meta:
        db_table = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    skin_type = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailed_description = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    usage_instructions = models.TextField(blank=True, null=True)
    allergy_warning = models.TextField(blank=True, null=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    price = models.FloatField()
    stock_quantity = models.IntegerField(default=0)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    class Meta:
        db_table = 'products'

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    
    class Meta:
        db_table = 'carts'

    @property
    def total_amount(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'cart_items'

    @property
    def total_price(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('PROCESSING', 'PROCESSING'),
        ('SHIPPED', 'SHIPPED'),
        ('DELIVERED', 'DELIVERED'),
        ('CANCELLED', 'CANCELLED'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.FloatField(default=0.0)
    shipping_address = models.TextField(blank=True, null=True)
    receiver_name = models.CharField(max_length=255, blank=True, null=True)
    receiver_phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_at_order = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'order_items'
        
    def get_total_price(self):
        return self.price_at_order * self.quantity


class PriceAdjustmentRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REJECTED', 'REJECTED'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_requests')
    old_price = models.FloatField()
    new_price = models.FloatField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'price_adjustment_requests'


class ChiNhanh(models.Model):
    ten_chi_nhanh = models.CharField(max_length=255)
    dia_chi = models.TextField(blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True, null=True)
    quan_ly = models.CharField(max_length=255, blank=True, null=True)
    trang_thai = models.BooleanField(default=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chi_nhanh'

    def __str__(self):
        return self.ten_chi_nhanh


class NhaCungCap(models.Model):
    ten_nha_cung_cap = models.CharField(max_length=255)
    nguoi_lien_he = models.CharField(max_length=255, blank=True, null=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    dia_chi = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'nha_cung_cap'

    def __str__(self):
        return self.ten_nha_cung_cap


class PhieuKho(models.Model):
    LOAI_PHIEU_CHOICES = (
        ('NHAP', 'Nhập kho'),
        ('XUAT', 'Xuất kho'),
    )
    ma_phieu = models.CharField(max_length=50, unique=True)
    loai_phieu = models.CharField(max_length=20, choices=LOAI_PHIEU_CHOICES, default='NHAP')
    chi_nhanh = models.ForeignKey(ChiNhanh, on_delete=models.CASCADE, related_name='danh_sach_phieu_kho')
    nha_cung_cap = models.ForeignKey(NhaCungCap, on_delete=models.SET_NULL, null=True, blank=True, related_name='danh_sach_phieu_kho')
    nhan_vien_nhan = models.CharField(max_length=255)
    nguoi_lap_phieu = models.ForeignKey(User, on_delete=models.CASCADE, related_name='phieu_kho_da_lap')
    ghi_chu = models.TextField(blank=True, null=True)
    tong_tien = models.FloatField(default=0.0)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'phieu_kho'

    def __str__(self):
        return f"{self.ma_phieu} - {self.get_loai_phieu_display()}"


class ChiTietPhieuKho(models.Model):
    phieu_kho = models.ForeignKey(PhieuKho, on_delete=models.CASCADE, related_name='chi_tiet')
    san_pham = models.ForeignKey(Product, on_delete=models.CASCADE)
    so_luong = models.IntegerField(default=1)
    don_gia = models.FloatField(default=0.0)
    thanh_tien = models.FloatField(default=0.0)

    class Meta:
        db_table = 'chi_tiet_phieu_kho'

    def tinh_thanh_tien(self):
        return self.so_luong * self.don_gia


class ComboSanPham(models.Model):
    ten_combo = models.CharField(max_length=255)
    mo_ta = models.TextField(blank=True, null=True)
    gia_combo = models.FloatField()
    gia_goc = models.FloatField(default=0.0)
    hinh_anh = models.CharField(max_length=500, blank=True, null=True)
    trang_thai = models.BooleanField(default=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'combo_san_pham'

    def __str__(self):
        return self.ten_combo

    def tinh_tong_gia_goc(self):
        return sum(chi_tiet.san_pham.price * chi_tiet.so_luong for chi_tiet in self.danh_sach_san_pham.all())

    def tinh_phan_tram_tiet_kiem(self):
        tong_goc = self.gia_goc or self.tinh_tong_gia_goc()
        if tong_goc > self.gia_combo and tong_goc > 0:
            return round((tong_goc - self.gia_combo) / tong_goc * 100)
        return 0

    def lay_hinh_anh(self):
        if self.hinh_anh:
            return self.hinh_anh
        dau_tien = self.danh_sach_san_pham.select_related('san_pham').first()
        if dau_tien and dau_tien.san_pham.image_url:
            return dau_tien.san_pham.image_url
        return '/static/images/no-image.png'


class ChiTietCombo(models.Model):
    combo = models.ForeignKey(ComboSanPham, on_delete=models.CASCADE, related_name='danh_sach_san_pham')
    san_pham = models.ForeignKey(Product, on_delete=models.CASCADE)
    so_luong = models.IntegerField(default=1)

    class Meta:
        db_table = 'chi_tiet_combo'

    def tinh_thanh_tien(self):
        return self.san_pham.price * self.so_luong

