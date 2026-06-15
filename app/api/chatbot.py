from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.schemas.chatbot import ChatbotRequest
from app.services.rag_chatbot_service import RagChatbotService


router = APIRouter(
    prefix="/chatbot",
    tags=["RAG Chatbot"]
)


@router.post("/rag")
def chat_with_rag(
    data: ChatbotRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return RagChatbotService.chat(
            db=db,
            ma_chuyen_di=data.ma_chuyen_di,
            message=data.message,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi chatbot RAG: {str(e)}"
        )