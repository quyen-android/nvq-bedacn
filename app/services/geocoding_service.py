import httpx


class GeocodingService:

    @staticmethod
    def search_location(query: str):
        if not query or not query.strip():
            raise ValueError("Vui lòng nhập tên địa điểm")

        url = "https://nominatim.openstreetmap.org/search"

        params = {
            "q": query.strip(),
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }

        headers = {
            "User-Agent": "nvq-travel-planner/1.0"
        }

        response = httpx.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            raise ValueError("Không thể lấy tọa độ")

        data = response.json()

        if not data:
            raise ValueError("Không tìm thấy tọa độ phù hợp")

        item = data[0]

        return {
            "display_name": item.get("display_name"),
            "vi_do": float(item.get("lat")),
            "kinh_do": float(item.get("lon"))
        }