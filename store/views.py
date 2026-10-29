from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, PriceAdjustmentRequest, ChiNhanh, NhaCungCap, PhieuKho, ChiTietPhieuKho, ComboSanPham, ChiTietCombo
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.paginator import Paginator
import os
from .market_basket import mba_analyzer

# --- Client Views ---
def landing_3d(request):
    return render(request, 'client/landing_3d.html')

def index(request):
    danh_sach_san_pham = Product.objects.all().order_by('-id')
    tu_khoa = request.GET.get('q')
    ma_danh_muc = request.GET.get('category_id')
    so_trang = request.GET.get('page', 1)

    if tu_khoa:
        danh_sach_san_pham = danh_sach_san_pham.filter(name__icontains=tu_khoa)
    if ma_danh_muc:
        try:
            danh_sach_san_pham = danh_sach_san_pham.filter(category_id=int(ma_danh_muc))
        except ValueError:
            pass

    phan_trang = Paginator(danh_sach_san_pham, 8)
    trang_hien_tai = phan_trang.get_page(so_trang)

    danh_sach_danh_muc = Category.objects.all()
    return render(request, 'client/index.html', {
        'products': trang_hien_tai,
        'categories': danh_sach_danh_muc,
        'q': tu_khoa,
        'cat_id': ma_danh_muc,
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    recommendations = mba_analyzer.get_product_recommendations(product.id, limit=4)
    return render(request, 'client/product-detail.html', {
        'product': product,
        'recommendations': recommendations
    })

@login_required(login_url='/login/')
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_recommendations = mba_analyzer.get_cart_recommendations(cart, limit=4)
    return render(request, 'client/cart.html', {
        'cart': cart,
        'cart_recommendations': cart_recommendations
    })

@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('productId')
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f"Đã thêm {product.name} vào giỏ hàng!")
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required(login_url='/login/')
def update_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')
        quantity = int(request.POST.get('quantity', 1))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        item.quantity = quantity
        item.save()
    return redirect('view_cart')

@login_required(login_url='/login/')
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('view_cart')

@login_required(login_url='/login/')
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Giỏ hàng của bạn đang trống.")
        return redirect('view_cart')
    
    total = sum(item.product.price * item.quantity for item in cart.items.all())
    return render(request, 'client/checkout.html', {'cart': cart, 'totalAmount': total})

@login_required(login_url='/login/')
def place_order(request):
    if request.method == 'POST':
        receiver_name = request.POST.get('receiverName')
        shipping_address = request.POST.get('shippingAddress')
        receiver_phone = request.POST.get('receiverPhone')
        
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            messages.error(request, "Giỏ hàng trống.")
            return redirect('view_cart')
        
        total = sum(item.product.price * item.quantity for item in cart.items.all())
        
        order = Order.objects.create(
            user=request.user,
            receiver_name=receiver_name,
            shipping_address=shipping_address,
            receiver_phone=receiver_phone,
            total_amount=total
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price_at_order=item.product.price,
                quantity=item.quantity
            )
            # Deduct stock
            item.product.stock_quantity -= item.quantity
            item.product.save()
            
        cart.items.all().delete()
        messages.success(request, f"Đặt hàng thành công! Mã đơn hàng: #{order.id}")
        return redirect('order_list')
    return redirect('checkout')

@login_required(login_url='/login/')
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'client/order-list.html', {'orders': orders})

@login_required(login_url='/login/')
def profile_view(request):
    if request.method == 'POST':
        request.user.phone = request.POST.get('phone')
        request.user.address = request.POST.get('address')
        request.user.email = request.POST.get('email')
        request.user.save()
        messages.success(request, "Cập nhật hồ sơ thành công!")
    return render(request, 'client/profile.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.role == 'ADMIN':
                    return redirect('admin_index')
                elif user.role == 'EMPLOYEE':
                    return redirect('employee_dashboard')
                return redirect('index')
            else:
                messages.error(request, "Tài khoản của bạn đã bị khóa.")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    return render(request, 'client/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại.")
            return render(request, 'client/register.html')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            phone=phone,
            address=address,
            role='CUSTOMER'
        )
        Cart.objects.create(user=user)
        messages.success(request, "Đăng ký thành công, vui lòng đăng nhập.")
        return redirect('login')
    return render(request, 'client/register.html')

# --- Admin Views ---
def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'ADMIN':
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view

def staff_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['ADMIN', 'EMPLOYEE']:
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view

@admin_required
def admin_index(request):
    don_hang_da_giao = Order.objects.filter(status='DELIVERED')
    tong_doanh_thu = sum(o.total_amount for o in don_hang_da_giao)
    
    thoi_gian_hien_tai = timezone.now()
    don_hang_thang_nay = don_hang_da_giao.filter(
        order_date__month=thoi_gian_hien_tai.month,
        order_date__year=thoi_gian_hien_tai.year
    )
    doanh_thu_thang_nay = sum(o.total_amount for o in don_hang_thang_nay)

    don_hang_moi_nhat = Order.objects.all().select_related('user').order_by('-order_date')[:8]
    san_pham_sap_het_kho = Product.objects.all().select_related('category').filter(stock_quantity__lte=15).order_by('stock_quantity')[:8]
    thanh_vien_moi = User.objects.all().order_by('-date_joined')[:6]
    combo_noi_bat = ComboSanPham.objects.all().prefetch_related('danh_sach_san_pham__san_pham').order_by('-ngay_tao')[:5]
    
    return render(request, 'admin/index.html', {
        'activePage': 'dashboard',
        'productCount': Product.objects.count(),
        'userCount': User.objects.count(),
        'orderCount': Order.objects.count(),
        'revenue': tong_doanh_thu,
        'monthly_revenue': doanh_thu_thang_nay,
        'don_hang_moi_nhat': don_hang_moi_nhat,
        'san_pham_sap_het_kho': san_pham_sap_het_kho,
        'thanh_vien_moi': thanh_vien_moi,
        'combo_noi_bat': combo_noi_bat,
    })

@admin_required
def admin_market_basket(request):
    analytics = mba_analyzer.get_dashboard_analytics()
    return render(request, 'admin/market-basket-analytics.html', {
        'activePage': 'mba',
        'analytics': analytics
    })

@admin_required
def admin_list_products(request):
    danh_sach_san_pham = Product.objects.all().select_related('category').order_by('-id')
    tu_khoa = request.GET.get('q', '').strip()
    so_trang = request.GET.get('page', 1)

    if tu_khoa:
        danh_sach_san_pham = danh_sach_san_pham.filter(
            Q(name__icontains=tu_khoa) |
            Q(brand__icontains=tu_khoa) |
            Q(category__name__icontains=tu_khoa)
        )

    phan_trang = Paginator(danh_sach_san_pham, 10)
    trang_hien_tai = phan_trang.get_page(so_trang)

    return render(request, 'admin/product-list.html', {
        'activePage': 'products',
        'products': trang_hien_tai,
        'tu_khoa': tu_khoa,
    })

@admin_required
def admin_add_product(request):
    return render(request, 'admin/product-form.html', {
        'activePage': 'products',
        'categories': Category.objects.all()
    })

@admin_required
def admin_save_product(request):
    if request.method == 'POST':
        pid = request.POST.get('id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stockQuantity')
        cat_id = request.POST.get('category.id') # Depending on thymeleaf translation
        if not cat_id:
            cat_id = request.POST.get('category')
            
        category = get_object_or_404(Category, id=cat_id)
        
        if pid:
            product = get_object_or_404(Product, id=pid)
            product.name = name
            product.description = description
            product.price = price
            product.stock_quantity = stock
            product.category = category
        else:
            product = Product(
                name=name,
                description=description,
                price=price,
                stock_quantity=stock,
                category=category
            )
            
        image = request.FILES.get('imageProduct')
        if image:
            fs = FileSystemStorage(location='e:/cosmetics-store/static/images/')
            filename = fs.save(image.name, image)
            product.image_url = '/images/' + filename
            
        product.save()
        messages.success(request, "Đã lưu sản phẩm thành công!")
        return redirect('admin_products')
    return redirect('admin_products')

@admin_required
def admin_delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Đã xóa sản phẩm thành công!")
    return redirect('admin_products')

@admin_required
def admin_edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'admin/product-form.html', {
        'activePage': 'products',
        'product': product,
        'categories': Category.objects.all()
    })

@admin_required
def admin_list_categories(request):
    return render(request, 'admin/category-list.html', {
        'activePage': 'categories',
        'categories': Category.objects.all()
    })

@admin_required
def admin_save_category(request):
    if request.method == 'POST':
        cid = request.POST.get('id')
        name = request.POST.get('name')
        if cid:
            cat = get_object_or_404(Category, id=cid)
            cat.name = name
            cat.save()
        else:
            Category.objects.create(name=name)
        messages.success(request, "Đã lưu danh mục thành công!")
    return redirect('admin_categories')

@admin_required
def admin_delete_category(request, id):
    try:
        cat = get_object_or_404(Category, id=id)
        cat.delete()
        messages.success(request, "Đã xóa danh mục thành công!")
    except Exception:
        messages.error(request, "Không thể xóa danh mục này!")
    return redirect('admin_categories')

@admin_required
def admin_list_orders(request):
    return render(request, 'admin/order-list.html', {
        'activePage': 'orders',
        'orders': Order.objects.all().order_by('-order_date')
    })

@admin_required
def admin_order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'admin/order-detail.html', {
        'activePage': 'orders',
        'order': order
    })

@admin_required
def admin_update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderId')
        status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save()
        messages.success(request, "Cập nhật trạng thái đơn hàng thành công!")
        return redirect('admin_order_detail', id=order_id)
    return redirect('admin_orders')

@admin_required
def admin_list_users(request):
    return render(request, 'admin/user-list.html', {
        'activePage': 'users',
        'users': User.objects.all()
    })

@admin_required
def admin_update_user_role(request):
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        role = request.POST.get('role')
        u = get_object_or_404(User, id=user_id)
        u.role = role
        u.save()
        messages.success(request, f"Đã cập nhật quyền cho: {u.username}")
    return redirect('admin_users')

@admin_required
def admin_toggle_user_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        u = get_object_or_404(User, id=user_id)
        u.is_active = not u.is_active
        u.save()
        messages.success(request, f"Đã {'Mở khóa' if u.is_active else 'Khóa'} tài khoản: {u.username}")
    return redirect('admin_users')

@admin_required
def admin_delete_user(request, id):
    u = get_object_or_404(User, id=id)
    u.delete()
    messages.success(request, "Xóa người dùng thành công!")
    return redirect('admin_users')

@admin_required
def admin_inventory(request):
    return render(request, 'admin/inventory-index.html', {
        'activePage': 'inventory',
        'products': Product.objects.all()
    })

@admin_required
def admin_add_stock(request):
    if request.method == 'POST':
        product_id = request.POST.get('productId')
        qty = int(request.POST.get('quantity', 0))
        p = get_object_or_404(Product, id=product_id)
        p.stock_quantity += qty
        p.save()
        messages.success(request, f"Đã cập nhật kho cho sản phẩm: {p.name}")
    return redirect('admin_inventory')


# --- Employee & Price Adjustment Views ---
@admin_required
def admin_create_employee(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên đăng nhập đã tồn tại.")
        else:
            User.objects.create_user(
                username=username,
                password=password,
                email=email,
                role='EMPLOYEE'
            )
            messages.success(request, "Tạo tài khoản nhân viên thành công!")
    return redirect('admin_users')

@admin_required
def admin_price_requests(request):
    requests = PriceAdjustmentRequest.objects.all().order_by('-created_at')
    return render(request, 'admin/price-requests.html', {
        'activePage': 'price_requests',
        'requests': requests
    })

@admin_required
def admin_handle_price_request(request, id, action):
    req = get_object_or_404(PriceAdjustmentRequest, id=id)
    if action == 'approve':
        req.status = 'APPROVED'
        req.product.price = req.new_price
        req.product.save()
        messages.success(request, "Đã phê duyệt yêu cầu điều chỉnh giá.")
    elif action == 'reject':
        req.status = 'REJECTED'
        messages.success(request, "Đã từ chối yêu cầu điều chỉnh giá.")
    req.save()
    return redirect('admin_price_requests')

@staff_required
def employee_dashboard(request):
    return render(request, 'employee/dashboard.html', {'activePage': 'dashboard'})

@staff_required
def employee_inventory(request):
    return render(request, 'employee/inventory.html', {
        'activePage': 'inventory',
        'products': Product.objects.all()
    })

@staff_required
def employee_create_order(request):
    if request.method == 'POST':
        product_id = request.POST.get('productId')
        quantity = int(request.POST.get('quantity', 1))
        customer_name = request.POST.get('customerName')
        customer_phone = request.POST.get('customerPhone')
        address = request.POST.get('address')
        
        product = get_object_or_404(Product, id=product_id)
        if product.stock_quantity >= quantity:
            order = Order.objects.create(
                user=request.user,
                receiver_name=customer_name,
                receiver_phone=customer_phone,
                shipping_address=address,
                total_amount=product.price * quantity,
                status='DELIVERED'
            )
            OrderItem.objects.create(
                order=order, product=product, price_at_order=product.price, quantity=quantity
            )
            product.stock_quantity -= quantity
            product.save()
            messages.success(request, "Tạo đơn hàng thành công!")
        else:
            messages.error(request, "Không đủ số lượng tồn kho!")
    return render(request, 'employee/create-order.html', {
        'activePage': 'create_order',
        'products': Product.objects.all()
    })

@staff_required
def employee_request_price(request):
    if request.method == 'POST':
        product_id = request.POST.get('productId')
        new_price = float(request.POST.get('newPrice', 0))
        reason = request.POST.get('reason', '')
        product = get_object_or_404(Product, id=product_id)
        
        PriceAdjustmentRequest.objects.create(
            product=product,
            requested_by=request.user,
            old_price=product.price,
            new_price=new_price,
            reason=reason
        )
        messages.success(request, "Gửi yêu cầu điều chỉnh giá thành công!")
        
    return render(request, 'employee/price-request.html', {
        'activePage': 'price_request',
        'products': Product.objects.all()
    })

@staff_required
def employee_manage_orders(request):
    orders = Order.objects.exclude(status='DELIVERED').order_by('order_date')
    return render(request, 'employee/manage-orders.html', {
        'activePage': 'manage_orders',
        'orders': orders
    })

@staff_required
def employee_update_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderId')
        status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)
        order.status = status
        order.save()
        messages.success(request, f"Đã cập nhật trạng thái đơn hàng #{order.id} thành {status}")
    return redirect('employee_manage_orders')


def lay_khung_giao_dien(nguoi_dung):
    if nguoi_dung.is_authenticated and nguoi_dung.role == 'ADMIN':
        return 'admin/layout.html'
    return 'employee/layout.html'


@staff_required
def danh_sach_phieu_kho(yeu_cau):
    danh_sach_phieu = PhieuKho.objects.all().select_related('chi_nhanh', 'nha_cung_cap', 'nguoi_lap_phieu').order_by('-ngay_tao')
    loai_phieu_loc = yeu_cau.GET.get('loai_phieu', '')
    chi_nhanh_loc = yeu_cau.GET.get('chi_nhanh_id', '')
    tu_khoa = yeu_cau.GET.get('q', '').strip()

    if loai_phieu_loc:
        danh_sach_phieu = danh_sach_phieu.filter(loai_phieu=loai_phieu_loc)
    if chi_nhanh_loc:
        danh_sach_phieu = danh_sach_phieu.filter(chi_nhanh_id=chi_nhanh_loc)
    if tu_khoa:
        danh_sach_phieu = danh_sach_phieu.filter(
            Q(ma_phieu__icontains=tu_khoa) |
            Q(nhan_vien_nhan__icontains=tu_khoa) |
            Q(nha_cung_cap__ten_nha_cung_cap__icontains=tu_khoa) |
            Q(chi_nhanh__ten_chi_nhanh__icontains=tu_khoa)
        )

    danh_sach_chi_nhanh = ChiNhanh.objects.all()
    danh_sach_nha_cung_cap = NhaCungCap.objects.all()

    return render(yeu_cau, 'inventory/danh_sach_phieu_kho.html', {
        'activePage': 'inventory_transactions',
        'khung_giao_dien': lay_khung_giao_dien(yeu_cau.user),
        'danh_sach_phieu': danh_sach_phieu,
        'danh_sach_chi_nhanh': danh_sach_chi_nhanh,
        'danh_sach_nha_cung_cap': danh_sach_nha_cung_cap,
        'loai_phieu_loc': loai_phieu_loc,
        'chi_nhanh_loc': chi_nhanh_loc,
        'tu_khoa': tu_khoa,
    })


@staff_required
def tao_phieu_kho(yeu_cau):
    if yeu_cau.method == 'POST':
        loai_phieu = yeu_cau.POST.get('loai_phieu', 'NHAP')
        chi_nhanh_id = yeu_cau.POST.get('chi_nhanh_id')
        nha_cung_cap_id = yeu_cau.POST.get('nha_cung_cap_id')
        nhan_vien_nhan = yeu_cau.POST.get('nhan_vien_nhan', '').strip()
        ghi_chu = yeu_cau.POST.get('ghi_chu', '').strip()

        danh_sach_id_san_pham = yeu_cau.POST.getlist('san_pham_id[]')
        danh_sach_so_luong = yeu_cau.POST.getlist('so_luong[]')
        danh_sach_don_gia = yeu_cau.POST.getlist('don_gia[]')

        if not chi_nhanh_id:
            messages.error(yeu_cau, "Vui lòng chọn chi nhánh.")
            return redirect('tao_phieu_kho')

        if not nhan_vien_nhan:
            nhan_vien_nhan = yeu_cau.user.username

        chi_nhanh = get_object_or_404(ChiNhanh, id=chi_nhanh_id)
        nha_cung_cap = None
        if nha_cung_cap_id and loai_phieu == 'NHAP':
            nha_cung_cap = NhaCungCap.objects.filter(id=nha_cung_cap_id).first()

        if not danh_sach_id_san_pham:
            messages.error(yeu_cau, "Vui lòng chọn ít nhất một sản phẩm.")
            return redirect('tao_phieu_kho')

        du_lieu_chi_tiet = []
        tong_tien_phieu = 0.0

        for vi_tri in range(len(danh_sach_id_san_pham)):
            ma_san_pham = danh_sach_id_san_pham[vi_tri]
            try:
                so_luong = int(danh_sach_so_luong[vi_tri])
                don_gia = float(danh_sach_don_gia[vi_tri])
            except (IndexError, ValueError):
                continue

            if so_luong <= 0:
                continue

            san_pham = get_object_or_404(Product, id=ma_san_pham)

            if loai_phieu == 'XUAT' and san_pham.stock_quantity < so_luong:
                messages.error(yeu_cau, f"Sản phẩm '{san_pham.name}' chỉ còn tồn {san_pham.stock_quantity}, không đủ để xuất {so_luong}.")
                return redirect('tao_phieu_kho')

            thanh_tien = so_luong * don_gia
            tong_tien_phieu += thanh_tien
            du_lieu_chi_tiet.append({
                'san_pham': san_pham,
                'so_luong': so_luong,
                'don_gia': don_gia,
                'thanh_tien': thanh_tien,
            })

        if not du_lieu_chi_tiet:
            messages.error(yeu_cau, "Danh sách sản phẩm không hợp lệ.")
            return redirect('tao_phieu_kho')

        thoi_gian_hien_tai = timezone.now()
        tien_to = 'PNK' if loai_phieu == 'NHAP' else 'PXK'
        ma_phieu = f"{tien_to}-{thoi_gian_hien_tai.strftime('%Y%m%d%H%M%S')}"

        phieu_kho = PhieuKho.objects.create(
            ma_phieu=ma_phieu,
            loai_phieu=loai_phieu,
            chi_nhanh=chi_nhanh,
            nha_cung_cap=nha_cung_cap,
            nhan_vien_nhan=nhan_vien_nhan,
            nguoi_lap_phieu=yeu_cau.user,
            ghi_chu=ghi_chu,
            tong_tien=tong_tien_phieu,
        )

        for muc in du_lieu_chi_tiet:
            ChiTietPhieuKho.objects.create(
                phieu_kho=phieu_kho,
                san_pham=muc['san_pham'],
                so_luong=muc['so_luong'],
                don_gia=muc['don_gia'],
                thanh_tien=muc['thanh_tien'],
            )
            if loai_phieu == 'NHAP':
                muc['san_pham'].stock_quantity += muc['so_luong']
            else:
                muc['san_pham'].stock_quantity -= muc['so_luong']
            muc['san_pham'].save()

        loai_hien_thi = "Nhập kho" if loai_phieu == 'NHAP' else "Xuất kho"
        messages.success(yeu_cau, f"Tạo phiếu {loai_hien_thi} thành công! Mã: {ma_phieu}")
        return redirect('chi_tiet_phieu_kho', ma_id=phieu_kho.id)

    danh_sach_chi_nhanh = ChiNhanh.objects.filter(trang_thai=True)
    danh_sach_nha_cung_cap = NhaCungCap.objects.all()
    danh_sach_san_pham = Product.objects.all().order_by('name')

    return render(yeu_cau, 'inventory/tao_phieu_kho.html', {
        'activePage': 'inventory_transactions',
        'khung_giao_dien': lay_khung_giao_dien(yeu_cau.user),
        'danh_sach_chi_nhanh': danh_sach_chi_nhanh,
        'danh_sach_nha_cung_cap': danh_sach_nha_cung_cap,
        'danh_sach_san_pham': danh_sach_san_pham,
    })


@staff_required
def chi_tiet_phieu_kho(yeu_cau, ma_id):
    phieu_kho = get_object_or_404(PhieuKho.objects.select_related('chi_nhanh', 'nha_cung_cap', 'nguoi_lap_phieu'), id=ma_id)
    chi_tiet_san_pham = phieu_kho.chi_tiet.select_related('san_pham').all()
    return render(yeu_cau, 'inventory/chi_tiet_phieu_kho.html', {
        'activePage': 'inventory_transactions',
        'khung_giao_dien': lay_khung_giao_dien(yeu_cau.user),
        'phieu_kho': phieu_kho,
        'chi_tiet_san_pham': chi_tiet_san_pham,
    })


@staff_required
def quan_ly_chi_nhanh(yeu_cau):
    danh_sach_chi_nhanh = ChiNhanh.objects.all().order_by('-ngay_tao')
    return render(yeu_cau, 'inventory/quan_ly_chi_nhanh.html', {
        'activePage': 'branch_management',
        'khung_giao_dien': lay_khung_giao_dien(yeu_cau.user),
        'danh_sach_chi_nhanh': danh_sach_chi_nhanh,
    })


@staff_required
def them_chi_nhanh(yeu_cau):
    if yeu_cau.method == 'POST':
        ten_chi_nhanh = yeu_cau.POST.get('ten_chi_nhanh', '').strip()
        dia_chi = yeu_cau.POST.get('dia_chi', '').strip()
        so_dien_thoai = yeu_cau.POST.get('so_dien_thoai', '').strip()
        quan_ly = yeu_cau.POST.get('quan_ly', '').strip()

        if ten_chi_nhanh:
            ChiNhanh.objects.create(
                ten_chi_nhanh=ten_chi_nhanh,
                dia_chi=dia_chi,
                so_dien_thoai=so_dien_thoai,
                quan_ly=quan_ly,
            )
            messages.success(yeu_cau, f"Đã thêm chi nhánh '{ten_chi_nhanh}' thành công!")
        else:
            messages.error(yeu_cau, "Vui lòng nhập tên chi nhánh.")
    return redirect('quan_ly_chi_nhanh')


@staff_required
def xoa_chi_nhanh(yeu_cau, ma_id):
    if yeu_cau.user.role != 'ADMIN':
        messages.error(yeu_cau, "Chỉ quản trị viên mới có quyền xóa chi nhánh.")
        return redirect('quan_ly_chi_nhanh')
    chi_nhanh = get_object_or_404(ChiNhanh, id=ma_id)
    ten = chi_nhanh.ten_chi_nhanh
    chi_nhanh.delete()
    messages.success(yeu_cau, f"Đã xóa chi nhánh '{ten}'!")
    return redirect('quan_ly_chi_nhanh')


@staff_required
def quan_ly_nha_cung_cap(yeu_cau):
    danh_sach_nha_cung_cap = NhaCungCap.objects.all().order_by('-ngay_tao')
    return render(yeu_cau, 'inventory/quan_ly_nha_cung_cap.html', {
        'activePage': 'supplier_management',
        'khung_giao_dien': lay_khung_giao_dien(yeu_cau.user),
        'danh_sach_nha_cung_cap': danh_sach_nha_cung_cap,
    })


@staff_required
def them_nha_cung_cap(yeu_cau):
    if yeu_cau.method == 'POST':
        ten_nha_cung_cap = yeu_cau.POST.get('ten_nha_cung_cap', '').strip()
        nguoi_lien_he = yeu_cau.POST.get('nguoi_lien_he', '').strip()
        so_dien_thoai = yeu_cau.POST.get('so_dien_thoai', '').strip()
        email = yeu_cau.POST.get('email', '').strip()
        dia_chi = yeu_cau.POST.get('dia_chi', '').strip()

        if ten_nha_cung_cap:
            NhaCungCap.objects.create(
                ten_nha_cung_cap=ten_nha_cung_cap,
                nguoi_lien_he=nguoi_lien_he,
                so_dien_thoai=so_dien_thoai,
                email=email,
                dia_chi=dia_chi,
            )
            messages.success(yeu_cau, f"Đã thêm nhà cung cấp '{ten_nha_cung_cap}' thành công!")
        else:
            messages.error(yeu_cau, "Vui lòng nhập tên nhà cung cấp.")
    return redirect('quan_ly_nha_cung_cap')


@staff_required
def xoa_nha_cung_cap(yeu_cau, ma_id):
    if yeu_cau.user.role != 'ADMIN':
        messages.error(yeu_cau, "Chỉ quản trị viên mới có quyền xóa nhà cung cấp.")
        return redirect('quan_ly_nha_cung_cap')
    nha_cung_cap = get_object_or_404(NhaCungCap, id=ma_id)
    ten = nha_cung_cap.ten_nha_cung_cap
    nha_cung_cap.delete()
    messages.success(yeu_cau, f"Đã xóa nhà cung cấp '{ten}'!")
    return redirect('quan_ly_nha_cung_cap')


@admin_required
def quan_ly_combo(yeu_cau):
    tu_khoa = yeu_cau.GET.get('q', '').strip()
    danh_sach_combo = ComboSanPham.objects.all().prefetch_related('danh_sach_san_pham__san_pham').order_by('-ngay_tao')

    if tu_khoa:
        danh_sach_combo = danh_sach_combo.filter(
            Q(ten_combo__icontains=tu_khoa) |
            Q(mo_ta__icontains=tu_khoa)
        )

    tong_so_combo = danh_sach_combo.count()
    so_combo_hoat_dong = danh_sach_combo.filter(trang_thai=True).count()

    return render(yeu_cau, 'admin/quan_ly_combo.html', {
        'activePage': 'combo_management',
        'danh_sach_combo': danh_sach_combo,
        'tu_khoa': tu_khoa,
        'tong_so_combo': tong_so_combo,
        'so_combo_hoat_dong': so_combo_hoat_dong,
    })


@admin_required
def tao_combo(yeu_cau):
    if yeu_cau.method == 'POST':
        ten_combo = yeu_cau.POST.get('ten_combo', '').strip()
        mo_ta = yeu_cau.POST.get('mo_ta', '').strip()
        gia_combo_chuoi = yeu_cau.POST.get('gia_combo', '0').strip()
        hinh_anh = yeu_cau.POST.get('hinh_anh', '').strip()
        danh_sach_id_san_pham = yeu_cau.POST.getlist('san_pham_id[]')
        danh_sach_so_luong = yeu_cau.POST.getlist('so_luong[]')

        if not ten_combo:
            messages.error(yeu_cau, "Vui lòng nhập tên combo.")
            return redirect('tao_combo')

        try:
            gia_combo = float(gia_combo_chuoi)
            if gia_combo <= 0:
                raise ValueError
        except ValueError:
            messages.error(yeu_cau, "Giá combo phải là số dương hợp lệ.")
            return redirect('tao_combo')

        if len(danh_sach_id_san_pham) < 2:
            messages.error(yeu_cau, "Gói combo cần kết hợp ít nhất 2 mặt hàng sản phẩm.")
            return redirect('tao_combo')

        tong_gia_goc = 0.0
        chi_tiet_hop_le = []

        for vi_tri in range(len(danh_sach_id_san_pham)):
            ma_san_pham = danh_sach_id_san_pham[vi_tri]
            try:
                so_luong = int(danh_sach_so_luong[vi_tri])
                if so_luong <= 0:
                    so_luong = 1
            except (ValueError, IndexError):
                so_luong = 1

            san_pham = Product.objects.filter(id=ma_san_pham).first()
            if san_pham:
                tong_gia_goc += san_pham.price * so_luong
                chi_tiet_hop_le.append((san_pham, so_luong))

        if len(chi_tiet_hop_le) < 2:
            messages.error(yeu_cau, "Cần chọn ít nhất 2 sản phẩm hợp lệ để tạo combo.")
            return redirect('tao_combo')

        combo_moi = ComboSanPham.objects.create(
            ten_combo=ten_combo,
            mo_ta=mo_ta,
            gia_combo=gia_combo,
            gia_goc=tong_gia_goc,
            hinh_anh=hinh_anh if hinh_anh else None,
            trang_thai=True
        )

        for san_pham, so_luong in chi_tiet_hop_le:
            ChiTietCombo.objects.create(
                combo=combo_moi,
                san_pham=san_pham,
                so_luong=so_luong
            )

        messages.success(yeu_cau, f"Đã tạo combo '{ten_combo}' thành công!")
        return redirect('quan_ly_combo')

    danh_sach_san_pham = Product.objects.all().select_related('category').order_by('name')
    danh_sach_id_chon_truoc = []
    tham_so_sp_ids = yeu_cau.GET.get('sp_ids', '')
    if tham_so_sp_ids:
        danh_sach_id_chon_truoc = [int(ma_so) for ma_so in tham_so_sp_ids.split(',') if ma_so.strip().isdigit()]

    ten_combo_goi_y = yeu_cau.GET.get('ten', '')

    return render(yeu_cau, 'admin/form_combo.html', {
        'activePage': 'combo_management',
        'danh_sach_san_pham': danh_sach_san_pham,
        'danh_sach_id_chon_truoc': danh_sach_id_chon_truoc,
        'ten_combo_goi_y': ten_combo_goi_y,
        'la_chinh_sua': False,
    })


@admin_required
def sua_combo(yeu_cau, ma_id):
    combo = get_object_or_404(ComboSanPham, id=ma_id)

    if yeu_cau.method == 'POST':
        ten_combo = yeu_cau.POST.get('ten_combo', '').strip()
        mo_ta = yeu_cau.POST.get('mo_ta', '').strip()
        gia_combo_chuoi = yeu_cau.POST.get('gia_combo', '0').strip()
        hinh_anh = yeu_cau.POST.get('hinh_anh', '').strip()
        danh_sach_id_san_pham = yeu_cau.POST.getlist('san_pham_id[]')
        danh_sach_so_luong = yeu_cau.POST.getlist('so_luong[]')

        if not ten_combo:
            messages.error(yeu_cau, "Vui lòng nhập tên combo.")
            return redirect('sua_combo', ma_id=ma_id)

        try:
            gia_combo = float(gia_combo_chuoi)
            if gia_combo <= 0:
                raise ValueError
        except ValueError:
            messages.error(yeu_cau, "Giá combo phải là số dương hợp lệ.")
            return redirect('sua_combo', ma_id=ma_id)

        if len(danh_sach_id_san_pham) < 2:
            messages.error(yeu_cau, "Gói combo cần kết hợp ít nhất 2 mặt hàng sản phẩm.")
            return redirect('sua_combo', ma_id=ma_id)

        tong_gia_goc = 0.0
        chi_tiet_hop_le = []

        for vi_tri in range(len(danh_sach_id_san_pham)):
            ma_san_pham = danh_sach_id_san_pham[vi_tri]
            try:
                so_luong = int(danh_sach_so_luong[vi_tri])
                if so_luong <= 0:
                    so_luong = 1
            except (ValueError, IndexError):
                so_luong = 1

            san_pham = Product.objects.filter(id=ma_san_pham).first()
            if san_pham:
                tong_gia_goc += san_pham.price * so_luong
                chi_tiet_hop_le.append((san_pham, so_luong))

        if len(chi_tiet_hop_le) < 2:
            messages.error(yeu_cau, "Cần chọn ít nhất 2 sản phẩm hợp lệ để lưu combo.")
            return redirect('sua_combo', ma_id=ma_id)

        combo.ten_combo = ten_combo
        combo.mo_ta = mo_ta
        combo.gia_combo = gia_combo
        combo.gia_goc = tong_gia_goc
        combo.hinh_anh = hinh_anh if hinh_anh else None
        combo.save()

        combo.danh_sach_san_pham.all().delete()
        for san_pham, so_luong in chi_tiet_hop_le:
            ChiTietCombo.objects.create(
                combo=combo,
                san_pham=san_pham,
                so_luong=so_luong
            )

        messages.success(yeu_cau, f"Đã cập nhật combo '{ten_combo}' thành công!")
        return redirect('quan_ly_combo')

    danh_sach_san_pham = Product.objects.all().select_related('category').order_by('name')
    danh_sach_chi_tiet_hien_tai = combo.danh_sach_san_pham.select_related('san_pham').all()
    danh_sach_id_chon_truoc = [chi_tiet.san_pham_id for chi_tiet in danh_sach_chi_tiet_hien_tai]
    ban_do_so_luong = {chi_tiet.san_pham_id: chi_tiet.so_luong for chi_tiet in danh_sach_chi_tiet_hien_tai}

    return render(yeu_cau, 'admin/form_combo.html', {
        'activePage': 'combo_management',
        'combo': combo,
        'danh_sach_san_pham': danh_sach_san_pham,
        'danh_sach_id_chon_truoc': danh_sach_id_chon_truoc,
        'ban_do_so_luong': ban_do_so_luong,
        'la_chinh_sua': True,
    })


@admin_required
def xoa_combo(yeu_cau, ma_id):
    combo = get_object_or_404(ComboSanPham, id=ma_id)
    ten_combo = combo.ten_combo
    combo.delete()
    messages.success(yeu_cau, f"Đã xóa gói combo '{ten_combo}' thành công!")
    return redirect('quan_ly_combo')


@admin_required
def doi_trang_thai_combo(yeu_cau, ma_id):
    combo = get_object_or_404(ComboSanPham, id=ma_id)
    combo.trang_thai = not combo.trang_thai
    combo.save()
    trang_thai_chuoi = "kích hoạt mở bán" if combo.trang_thai else "tạm ẩn"
    messages.success(yeu_cau, f"Đã {trang_thai_chuoi} combo '{combo.ten_combo}'!")
    return redirect('quan_ly_combo')


