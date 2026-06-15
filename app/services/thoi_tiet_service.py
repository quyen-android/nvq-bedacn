import requests

from datetime import date, datetime, timedelta

from app.models.chuyen_di import ChuyenDi
from app.models.thoi_tiet_chuyen_di import ThoiTietChuyenDi


class ThoiTietService:

    CACHE_HOURS = 6
    MAX_FORECAST_DAYS = 16

    WEATHER_MAP = {
        0: ("Trời quang", "sunny"),
        1: ("Ít mây", "partly_cloudy"),
        2: ("Có mây", "cloudy"),
        3: ("Nhiều mây", "cloudy"),

        45: ("Sương mù", "fog"),
        48: ("Sương mù đóng băng", "fog"),

        51: ("Mưa phùn nhẹ", "drizzle"),
        53: ("Mưa phùn", "drizzle"),
        55: ("Mưa phùn dày", "drizzle"),
        56: ("Mưa phùn đóng băng nhẹ", "drizzle"),
        57: ("Mưa phùn đóng băng", "drizzle"),

        61: ("Mưa nhẹ", "rain"),
        63: ("Mưa vừa", "rain"),
        65: ("Mưa lớn", "rain"),
        66: ("Mưa đóng băng nhẹ", "rain"),
        67: ("Mưa đóng băng", "rain"),

        71: ("Tuyết nhẹ", "snow"),
        73: ("Tuyết vừa", "snow"),
        75: ("Tuyết lớn", "snow"),
        77: ("Hạt tuyết", "snow"),

        80: ("Mưa rào nhẹ", "rain"),
        81: ("Mưa rào", "rain"),
        82: ("Mưa rào lớn", "rain"),

        85: ("Mưa tuyết nhẹ", "snow"),
        86: ("Mưa tuyết lớn", "snow"),

        95: ("Dông", "storm"),
        96: ("Dông có mưa đá nhẹ", "storm"),
        99: ("Dông có mưa đá lớn", "storm"),
    }

    @classmethod
    def should_update_weather(cls, db, chuyen_di):
        if not chuyen_di or not chuyen_di.ngay_di or not chuyen_di.ngay_ve:
            return False

        today = date.today()

        days_left = (chuyen_di.ngay_di - today).days

        if days_left > cls.MAX_FORECAST_DAYS:
            return False

        latest = (
            db.query(ThoiTietChuyenDi)
            .filter(
                ThoiTietChuyenDi.ma_chuyen_di == chuyen_di.ma_chuyen_di
            )
            .order_by(ThoiTietChuyenDi.ngay_cap_nhat.desc())
            .first()
        )

        if not latest:
            return True

        if not latest.ngay_cap_nhat:
            return True

        expired_time = datetime.utcnow() - timedelta(hours=cls.CACHE_HOURS)

        return latest.ngay_cap_nhat.replace(tzinfo=None) < expired_time

    @classmethod
    def get_weather_label(cls, code):
        return cls.WEATHER_MAP.get(
            int(code or 0),
            ("Không rõ", "unknown")
        )

    @classmethod
    def fetch_open_meteo(cls, latitude, longitude, start_date, end_date):
        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "Asia/Ho_Chi_Minh",
            "start_date": str(start_date),
            "end_date": str(end_date),
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    @classmethod
    def update_trip_weather(
        cls,
        db,
        ma_chuyen_di,
        force=False
    ):
        chuyen_di = (
            db.query(ChuyenDi)
            .filter(ChuyenDi.ma_chuyen_di == ma_chuyen_di)
            .first()
        )

        if not chuyen_di:
            raise ValueError("Không tìm thấy chuyến đi")

        if not chuyen_di.tinh_den:
            raise ValueError("Chuyến đi chưa có tỉnh đến")

        if not chuyen_di.tinh_den.vi_do or not chuyen_di.tinh_den.kinh_do:
            raise ValueError("Tỉnh đến chưa có tọa độ")

        if not force and not cls.should_update_weather(db, chuyen_di):
            return cls.get_trip_weather(db, ma_chuyen_di)

        today = date.today()

        if (chuyen_di.ngay_di - today).days > cls.MAX_FORECAST_DAYS:
            return cls.get_trip_weather(db, ma_chuyen_di)

        data = cls.fetch_open_meteo(
            latitude=float(chuyen_di.tinh_den.vi_do),
            longitude=float(chuyen_di.tinh_den.kinh_do),
            start_date=chuyen_di.ngay_di,
            end_date=chuyen_di.ngay_ve
        )

        daily = data.get("daily", {})

        dates = daily.get("time", [])
        weather_codes = daily.get("weather_code", [])
        temp_maxs = daily.get("temperature_2m_max", [])
        temp_mins = daily.get("temperature_2m_min", [])

        for index, day_str in enumerate(dates):
            ngay = datetime.strptime(day_str, "%Y-%m-%d").date()

            code = weather_codes[index] if index < len(weather_codes) else 0
            mo_ta, icon = cls.get_weather_label(code)

            nhiet_do_min = temp_mins[index] if index < len(temp_mins) else None
            nhiet_do_max = temp_maxs[index] if index < len(temp_maxs) else None

            nhiet_do = None

            if nhiet_do_min is not None and nhiet_do_max is not None:
                nhiet_do = round((nhiet_do_min + nhiet_do_max) / 2, 1)

            record = (
                db.query(ThoiTietChuyenDi)
                .filter(
                    ThoiTietChuyenDi.ma_chuyen_di == chuyen_di.ma_chuyen_di,
                    ThoiTietChuyenDi.ngay == ngay
                )
                .first()
            )

            if not record:
                record = ThoiTietChuyenDi(
                    ma_chuyen_di=chuyen_di.ma_chuyen_di,
                    ngay=ngay
                )

                db.add(record)

            record.nhiet_do = nhiet_do
            record.nhiet_do_min = nhiet_do_min
            record.nhiet_do_max = nhiet_do_max
            record.mo_ta = mo_ta
            record.icon = icon
            record.ngay_cap_nhat = datetime.utcnow()

        db.commit()

        return cls.get_trip_weather(db, ma_chuyen_di)

    @staticmethod
    def get_trip_weather(db, ma_chuyen_di):
        items = (
            db.query(ThoiTietChuyenDi)
            .filter(
                ThoiTietChuyenDi.ma_chuyen_di == ma_chuyen_di
            )
            .order_by(ThoiTietChuyenDi.ngay.asc())
            .all()
        )

        return [
            {
                "ma_thoi_tiet": str(item.ma_thoi_tiet),
                "ma_chuyen_di": str(item.ma_chuyen_di),
                "ngay": str(item.ngay),
                "nhiet_do": item.nhiet_do,
                "nhiet_do_min": item.nhiet_do_min,
                "nhiet_do_max": item.nhiet_do_max,
                "mo_ta": item.mo_ta,
                "icon": item.icon,
                "ngay_cap_nhat": item.ngay_cap_nhat
            }
            for item in items
        ]