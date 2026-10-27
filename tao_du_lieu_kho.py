import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_cosmetics_store.settings')
django.setup()

from store.models import ChiNhanh, NhaCungCap, PhieuKho, ChiTietPhieuKho, Product, User

def tao_du_lieu_kho():
    nguoi_dung_quan_tri = User.objects.filter(role='ADMIN').first()
    if not nguoi_dung_quan_tri:
        nguoi_dung_quan_tri = User.objects.first()

    danh_sach_chi_nhanh_mau = [
        {
            'ten_chi_nhanh': 'Chi nhánh Quận 1 (Trụ sở chính)',
            'dia_chi': '123 Đường Đồng Khởi, Phường Bến Nghé, Quận 1, TP. HCM',
            'so_dien_thoai': '028 3822 9988',
            'quan_ly': 'Nguyễn Văn Quản Lý',
        },
        {
            'ten_chi_nhanh': 'Chi nhánh Cầu Giấy - Hà Nội',
            'dia_chi': '45 Đường Cầu Giấy, Phường Quan Hoa, Quận Cầu Giấy, Hà Nội',
            'so_dien_thoai': '024 3766 5544',
            'quan_ly': 'Trần Thị Trưởng Kho',
        },
        {
            'ten_chi_nhanh': 'Chi nhánh Hải Châu - Đà Nẵng',
            'dia_chi': '78 Đường Nguyễn Văn Linh, Quận Hải Châu, Đà Nẵng',
            'so_dien_thoai': '0236 3888 777',
            'quan_ly': 'Lê Hoàng Điều Phối',
        }
    ]

    for thong_tin in danh_sach_chi_nhanh_mau:
        ChiNhanh.objects.get_or_create(
            ten_chi_nhanh=thong_tin['ten_chi_nhanh'],
            defaults=thong_tin
        )

    danh_sach_nha_cung_cap_mau = [
        {
            'ten_nha_cung_cap': 'Công Ty TNHH Mỹ Phẩm L\'Oréal Việt Nam',
            'nguoi_lien_he': 'Phạm Thu Hà',
            'so_dien_thoai': '0903123456',
            'email': 'contact@loreal.vn',
            'dia_chi': 'Tầng 12, Tòa nhà Vincom Center, 72 Lê Thánh Tôn, Quận 1, TP. HCM',
        },
        {
            'ten_nha_cung_cap': 'Công Ty Phân Phối Mỹ Phẩm AmorePacific',
            'nguoi_lien_he': 'Kim Min Joon',
            'so_dien_thoai': '0918765432',
            'email': 'support@amorepacific.vn',
            'dia_chi': 'Tòa nhà Landmark 81, Bình Thạnh, TP. HCM',
        },
        {
            'ten_nha_cung_cap': 'Nhà Cung Cấp Dược Mỹ Phẩm La Roche-Posay',
            'nguoi_lien_he': 'Đặng Quốc Huy',
            'so_dien_thoai': '0988554433',
            'email': 'sales@larocheposay.vn',
            'dia_chi': 'Số 10 Hai Bà Trưng, Quận Hoàn Kiếm, Hà Nội',
        }
    ]

    for thong_tin in danh_sach_nha_cung_cap_mau:
        NhaCungCap.objects.get_or_create(
            ten_nha_cung_cap=thong_tin['ten_nha_cung_cap'],
            defaults=thong_tin
        )

    chi_nhanh_dau = ChiNhanh.objects.first()
    nha_cung_cap_dau = NhaCungCap.objects.first()
    san_pham_dau = Product.objects.first()

    if chi_nhanh_dau and nha_cung_cap_dau and san_pham_dau and nguoi_dung_quan_tri and not PhieuKho.objects.exists():
        phieu_nhap = PhieuKho.objects.create(
            ma_phieu='PNK-20261027090000',
            loai_phieu='NHAP',
            chi_nhanh=chi_nhanh_dau,
            nha_cung_cap=nha_cung_cap_dau,
            nhan_vien_nhan='Nguyễn Văn Nhân Viên',
            nguoi_lap_phieu=nguoi_dung_quan_tri,
            ghi_chu='Nhập bổ sung đầu đợt từ nhà phân phối',
            tong_tien=san_pham_dau.price * 50
        )
        ChiTietPhieuKho.objects.create(
            phieu_kho=phieu_nhap,
            san_pham=san_pham_dau,
            so_luong=50,
            don_gia=san_pham_dau.price,
            thanh_tien=san_pham_dau.price * 50
        )
        san_pham_dau.stock_quantity += 50
        san_pham_dau.save()

if __name__ == '__main__':
    tao_du_lieu_kho()
