from app.repositories import dia_diem_repo, yeu_thich_repo


def get_dia_diem_list(db, current_user=None, **filters):
    data = dia_diem_repo.filter_dia_diem(db, **filters)

    favorite_ids = []

    if current_user:
        favs = yeu_thich_repo.get_favorite_ids(
            db,
            current_user.ma_nguoi_dung  
        )
        favorite_ids = [f for f in favs]

    result = []

    for item in data:
        result.append({
            "ma_dia_diem": str(item.ma_dia_diem),
            "ten": item.ten,
            "danh_gia": item.danh_gia,
            "gia_trung_binh": item.gia_trung_binh,
            "is_favorite": item.ma_dia_diem in favorite_ids
        })

    return result