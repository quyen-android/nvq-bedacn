from app.models.refresh_token import RefreshToken
from datetime import datetime

class TokenRepository:
    def create(self, db, ma_nguoi_dung, ma_token, thoi_gian_het_han):
        rt = RefreshToken(
            ma_nguoi_dung = ma_nguoi_dung,
            ma_token = ma_token,
            thoi_gian_het_han = thoi_gian_het_han
        )

        db.add(rt)
        db.commit()
        db.refresh(rt)
        return rt
    
    def get(self, db, ma_token):
        return db.query(RefreshToken).filter(RefreshToken.ma_token == ma_token).first()
    
    def revoke(self, db, ma_token):
        rt = self.get(db, ma_token)
        if rt:
            rt.da_thu_hoi = True
            db.commit()