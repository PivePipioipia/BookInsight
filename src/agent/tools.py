import json
import sqlite3
from typing import Type, Any
from pydantic import BaseModel, Field, PrivateAttr
from langchain_core.tools import BaseTool

from config import SQL_DB_PATH
from retriever.smart_retriever import SmartRetriever

# SmartRAGTool
class SmartRAGInput(BaseModel):
    query: str = Field(description="Một câu hỏi hoặc chủ đề để tìm kiếm sách.")

class SmartRAGTool(BaseTool):
    """
    Một Tool cho phép Agent sử dụng SmartRetriever (RAG-Fusion)
    để tìm kiếm thông tin cho sách dựa trên ngữ nghĩa.
    """
    name: str = "smart_book_retriever" 
    description: str = (
        "Rất hữu ích khi cần trả lời câu hỏi về nội dung sách, mô tả sách, "
        "tiểu sử tác giả, gợi ý sách theo chủ đề."
    )
    args_schema: Type[BaseModel] = SmartRAGInput

    _rag_engine: SmartRetriever = PrivateAttr()

    def __init__(self, rag_engine: SmartRetriever, **data):
        super().__init__(**data)
        self._rag_engine = rag_engine

    def _run(self, query: str) -> str:
        print(f"\n[SmartRAGTool] đang chạy với câu hỏi: {query}")
        try:
            results = self._rag_engine.retrieve(query, top_k=3)
            return json.dumps(results, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Lỗi khi chạy SmartRAGTool: {e}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

# SavePreferenceTool 
class SavePreferenceInput(BaseModel):
    preference_type: str = Field(description="Loại sở thích (ví dụ: 'author', 'category', 'topic').")
    preference_value: str = Field(description="Giá trị của sở thích (ví dụ: 'Robert C.Martin', 'Science Fiction').")

class SavePreferenceTool(BaseTool):
    """
    Một Tool cho phép Agent LƯU LẠI sở thích của người dùng (như tác giả yêu thích, thể loại yêu thích,...) vào database.
    """
    name: str = "save_user_preference"
    description: str = (
        "Rất hữu ích khi người dùng BÀY TỎ một sở thích cụ thể. "
        "Dùng Tool này để GHI NHỚ tác giả yêu thích, thể loại yêu thích, ..."
        "hoặc chủ đề mà người dùng quan tâm."
    )
    args_schema: Type[BaseModel] = SavePreferenceInput

    def _run(self, preference_type: str, preference_value: str) -> str:
        print(f"\n[SavePreferenceTool] Đang lưu: {preference_type} = {preference_value}")
        user_id = 1 #mặc định cho user_id = 1
        try:
            insert_sql = "INSERT OR IGNORE INTO user_preferences (user_id, preference_type, preference_value) VALUES (?, ?, ?)"
            conn = sqlite3.connect(SQL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute(insert_sql, (user_id, preference_type, preference_value))
            conn.commit()
            conn.close()
            return f"Đã lưu thành công sở thích :{preference_type} = {preference_value}."
        except Exception as e:
            return f"Lỗi khi lưu sở thích: {e}"

    async def _arun(self, preference_type: str, preference_value: str) -> str:
        return self._run(preference_type, preference_value)

# GetPersonalizedRecommendationTool 

class GetRecommendationInput(BaseModel):
    pass

class GetPersonalizedRecommendationTool(BaseTool):
    """
    Một Tool cho phép Agent GỢI Ý sách DỰA TRÊN sở thích đã lưu của người dùng.
    """
    name: str = "get_personalized_recommendation"
    description: str = (
        "Rất hữu ích khi người dùng hỏi gợi ý sách CHUNG CHUNG (ví dụ: 'gợi ý cho tôi một cuốn sách'). "
        "Tool này sẽ tự động tìm sách dựa trên sở thích (tác giả, thể loại) đã lưu của người dùng."
    )
    args_schema: Type[BaseModel] = GetRecommendationInput
    
    _rag_tool: BaseTool = PrivateAttr()
    
    def __init__(self, rag_tool: BaseTool, **data):
        super().__init__(**data)
        self._rag_tool = rag_tool
    
    def _run(self) -> str:
        print(f"\n[GetRecommendationTool] ... Đang tìm sở thích đã lưu...")
        user_id = 1
        preferences = []
        try:
            conn = sqlite3.connect(SQL_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT preference_type, preference_value FROM user_preferences WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return "Tôi chưa biết sở thích của bạn. Hãy nói cho tôi biết bạn thích tác giả hoặc thể loại nào!"
            
            for row in rows:
                preferences.append(f"{row[0]} {row[1]}")

        except Exception as e:
            return f"Lỗi khi đọc sở thích: {e}"

        query_prompt = "Tìm sách dựa trên các sở thích sau: " + " AND ".join(preferences)
        print(f"[GetRecommendationTool] Đã tạo query cá nhân hóa: '{query_prompt}'")
        
        print("[GetRecommendationTool] Đang gọi SmartRAGTool để tìm sách...")
        return self._rag_tool.run(query_prompt)

    async def _arun(self) -> str:
        return self._run()