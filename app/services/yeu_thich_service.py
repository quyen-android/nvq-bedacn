from app.repositories import yeu_thich_repo


def toggle_favorite(db, current_user, dia_diem_id):
    return yeu_thich_repo.toggle_favorite(
        db,
        current_user.ma_nguoi_dung,
        dia_diem_id
    )


def get_my_favorites(db, current_user):
    
    return yeu_thich_repo.get_my_favorites(
        db,
        current_user.ma_nguoi_dung
    )
