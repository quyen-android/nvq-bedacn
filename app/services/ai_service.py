from app.services.rag_service import RagService
from app.ai.prompt import PromptBuilder
from app.ai.llm import LLMService


class AIService:

    @staticmethod
    def generate_itinerary(db, request):

        # 🔥 tạo query text cho semantic search
        search_query = f"""
        Loại du lịch: {' '.join(request.loai_du_lich)}

        Yêu cầu:
        {' '.join(request.yeu_cau_dac_biet)}

        Ẩm thực:
        {' '.join(request.so_thich_am_thuc)}
        """

        # 🔥 search chroma
        rag_results = RagService.search_places(
            search_query
        )

        documents = rag_results["documents"][0]

        context = "\n".join(documents)

        prompt = PromptBuilder.build_itinerary_prompt(
            request,
            context
        )

        llm_response = LLMService.generate(prompt)

        return {
            "message": "AI generated itinerary",
            "data": llm_response
        }