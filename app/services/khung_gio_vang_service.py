from datetime import time
from datetime import timedelta
from sqlalchemy import text

from fastapi import HTTPException

from app.models.khung_gio_vang import KhungGioVang

from app.repositories import (
    khung_gio_vang_repo,
    dia_diem_repo
)


class KhungGioVangService:

    @staticmethod
    def _parse_time(value):
        if not value:
            return None

        if isinstance(value, time):
            return value

        try:
            hour, minute = str(value).split(":")[:2]

            return time(
                int(hour),
                int(minute)
            )

        except Exception:
            raise HTTPException(
                400,
                "Giờ không hợp lệ"
            )

    @staticmethod
    def _validate_month(
        thang_bat_dau,
        thang_ket_thuc
    ):
        if thang_bat_dau < 1 or thang_bat_dau > 12:
            raise HTTPException(
                400,
                "Tháng bắt đầu phải từ 1 đến 12"
            )

        if thang_ket_thuc < 1 or thang_ket_thuc > 12:
            raise HTTPException(
                400,
                "Tháng kết thúc phải từ 1 đến 12"
            )

    @staticmethod
    def _validate_time_range(
        gio_bat_dau,
        gio_ket_thuc
    ):
        if not gio_bat_dau or not gio_ket_thuc:
            raise HTTPException(
                400,
                "Vui lòng nhập giờ bắt đầu và giờ kết thúc"
            )

        if gio_bat_dau >= gio_ket_thuc:
            raise HTTPException(
                400,
                "Giờ bắt đầu phải nhỏ hơn giờ kết thúc"
            )

    @staticmethod
    def _validate_place(
        db,
        ma_dia_diem
    ):
        dia_diem = dia_diem_repo.get_by_id(
            db,
            ma_dia_diem
        )

        if not dia_diem:
            raise HTTPException(
                404,
                "Không tìm thấy địa điểm"
            )

        return dia_diem

    @classmethod
    def get_all(cls, db):
        return khung_gio_vang_repo.get_all(
            db
        )

    @classmethod
    def get_by_id(
        cls,
        db,
        ma_khung_gio
    ):
        item = khung_gio_vang_repo.get_by_id(
            db,
            ma_khung_gio
        )

        if not item:
            raise HTTPException(
                404,
                "Không tìm thấy khung giờ vàng"
            )

        return item

    @classmethod
    def get_by_dia_diem(
        cls,
        db,
        ma_dia_diem
    ):
        cls._validate_place(
            db,
            ma_dia_diem
        )

        return khung_gio_vang_repo.get_by_dia_diem(
            db,
            ma_dia_diem
        )

    @classmethod
    def create(
        cls,
        db,
        data
    ):
        cls._validate_place(
            db,
            data.ma_dia_diem
        )

        cls._validate_month(
            data.thang_bat_dau,
            data.thang_ket_thuc
        )

        gio_bat_dau = cls._parse_time(
            data.gio_bat_dau
        )

        gio_ket_thuc = cls._parse_time(
            data.gio_ket_thuc
        )

        cls._validate_time_range(
            gio_bat_dau,
            gio_ket_thuc
        )

        item = KhungGioVang(
            ma_dia_diem=data.ma_dia_diem,
            thang_bat_dau=data.thang_bat_dau,
            thang_ket_thuc=data.thang_ket_thuc,
            gio_bat_dau=gio_bat_dau,
            gio_ket_thuc=gio_ket_thuc
        )

        item = khung_gio_vang_repo.create(
            db,
            item
        )

        db.commit()
        db.refresh(item)

        return item

    @classmethod
    def update(
        cls,
        db,
        ma_khung_gio,
        data
    ):
        item = cls.get_by_id(
            db,
            ma_khung_gio
        )

        new_ma_dia_diem = (
            data.ma_dia_diem
            if data.ma_dia_diem is not None
            else item.ma_dia_diem
        )

        cls._validate_place(
            db,
            new_ma_dia_diem
        )

        new_thang_bat_dau = (
            data.thang_bat_dau
            if data.thang_bat_dau is not None
            else item.thang_bat_dau
        )

        new_thang_ket_thuc = (
            data.thang_ket_thuc
            if data.thang_ket_thuc is not None
            else item.thang_ket_thuc
        )

        cls._validate_month(
            new_thang_bat_dau,
            new_thang_ket_thuc
        )

        new_gio_bat_dau = (
            cls._parse_time(data.gio_bat_dau)
            if data.gio_bat_dau is not None
            else item.gio_bat_dau
        )

        new_gio_ket_thuc = (
            cls._parse_time(data.gio_ket_thuc)
            if data.gio_ket_thuc is not None
            else item.gio_ket_thuc
        )

        cls._validate_time_range(
            new_gio_bat_dau,
            new_gio_ket_thuc
        )

        item.ma_dia_diem = new_ma_dia_diem
        item.thang_bat_dau = new_thang_bat_dau
        item.thang_ket_thuc = new_thang_ket_thuc
        item.gio_bat_dau = new_gio_bat_dau
        item.gio_ket_thuc = new_gio_ket_thuc

        db.commit()
        db.refresh(item)

        return item

    @classmethod
    def delete(
        cls,
        db,
        ma_khung_gio
    ):
        item = cls.get_by_id(
            db,
            ma_khung_gio
        )

        khung_gio_vang_repo.delete(
            db,
            item
        )

        db.commit()

        return {
            "message": "Xóa khung giờ vàng thành công"
        }
    
    @staticmethod
    def get_place_id(place):
        if isinstance(place, dict):
            return (
                place.get("ma_dia_diem")
                or place.get("metadata", {}).get("ma_dia_diem")
                or place.get("metadata", {}).get("id")
            )

        return getattr(place, "ma_dia_diem", None)

    @classmethod
    def lock_golden_hour_places(cls, db, days_plan, start_date):
        for day in days_plan:
            ngay_thuc_te = start_date + timedelta(
                days=day["day"] - 1
            )

            thang_hien_tai = ngay_thuc_te.month
            locked_places = []

            for place in day.get("places", []):
                ma_dia_diem = cls.get_place_id(place)

                if not ma_dia_diem:
                    continue

                query = text("""
                    SELECT 
                        gio_bat_dau,
                        gio_ket_thuc,
                        thang_bat_dau,
                        thang_ket_thuc
                    FROM khung_gio_vang
                    WHERE ma_dia_diem = :ma_dia_diem
                """)

                rows = db.execute(
                    query,
                    {"ma_dia_diem": ma_dia_diem}
                ).fetchall()

                for row in rows:
                    thang_bat_dau = row.thang_bat_dau
                    thang_ket_thuc = row.thang_ket_thuc

                    if thang_bat_dau <= thang_ket_thuc:
                        hop_le = (
                            thang_bat_dau
                            <= thang_hien_tai
                            <= thang_ket_thuc
                        )
                    else:
                        hop_le = (
                            thang_hien_tai >= thang_bat_dau
                            or thang_hien_tai <= thang_ket_thuc
                        )

                    if hop_le:
                        locked_places.append({
                            "place": place,
                            "locked_start": row.gio_bat_dau,
                            "locked_end": row.gio_ket_thuc
                        })
                        break

            day["locked_places"] = locked_places

        return days_plan
    