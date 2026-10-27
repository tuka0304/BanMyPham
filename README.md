# Aeterna - Website Mỹ Phẩm Cao Cấp

Hệ thống thương mại điện tử mỹ phẩm cao cấp xây dựng trên nền tảng Django, bao gồm đầy đủ tính năng cho Khách hàng, Nhân viên và Quản trị viên.

## Các Tính Năng Nổi Bật

- **Dành Cho Khách Hàng**:
  - Giao diện Landing Page 3D hiện đại, hiệu ứng thị giác sang trọng.
  - Khám phá danh mục sản phẩm, tìm kiếm, lọc theo danh mục và phân trang tiện lợi.
  - Xem chi tiết sản phẩm và gợi ý sản phẩm liên quan thông qua thuật toán Phân tích giỏ hàng (Market Basket Analysis).
  - Giỏ hàng, cập nhật số lượng và đặt hàng trực tuyến.
  - Quản lý lịch sử đơn hàng và thông tin tài khoản cá nhân.

- **Dành Cho Quản Trị Viên (Admin) & Nhân Viên (Employee)**:
  - Bảng điều khiển tổng quan (Dashboard) trực quan.
  - Quản lý danh mục sản phẩm và danh sách sản phẩm (có tìm kiếm và phân trang).
  - Quản lý đơn hàng và cập nhật trạng thái đơn hàng.
  - Quản lý phân quyền tài khoản người dùng (Admin, Employee, Customer).
  - Phân tích giỏ hàng nâng cao (Market Basket Analytics - MBA).
  - Hệ thống Quản lý Xuất / Nhập Kho: Lập phiếu nhập kho từ nhà cung cấp, lập phiếu xuất kho theo chi nhánh, ghi nhận nhân viên nhận hàng, tự động đồng bộ số lượng tồn kho.
  - Quản lý Chi Nhánh cửa hàng và thông tin liên hệ.
  - Quản lý Danh Sách Nhà Cung Cấp đối tác.

## Cài Đặt & Chạy Thử

1. Kích hoạt môi trường ảo (nếu có):
```bash
python -m venv venv
venv\Scripts\activate
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Áp dụng cơ sở dữ liệu:
```bash
python manage.py migrate
```

4. Nạp dữ liệu mẫu ban đầu:
```bash
python load_products.py
python tao_du_lieu_kho.py
```

5. Khởi chạy máy chủ:
```bash
python manage.py runserver
```
Truy cập hệ thống tại: `http://127.0.0.1:8000/`
