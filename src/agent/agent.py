# Imports từ LangChain 
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

# Imports từ Project 
from config import SQL_DB_PATH, LLM_MODEL
from retriever.smart_retriever import SmartRetriever
from agent.tools import (
    SmartRAGTool,
    SavePreferenceTool,
    GetPersonalizedRecommendationTool
)


AGENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", (
            "Bạn là 'BookInsight', một trợ lý AI thông thái và cá nhân hóa. "
            "Bạn phải luôn suy nghĩ TỪNG BƯỚC MỘT.\n"
            
            "Bạn có 4 công cụ:\n"
            "1. 'smart_book_retriever' (RAG Tool): Dùng cho câu hỏi MỞ (tóm tắt, nội dung, tiểu sử, gợi ý theo chủ đề).\n"
            "2. 'sql_tool' (SQL Tool): Dùng cho câu hỏi CỤ THỂ (giá, rating, đếm, so sánh, max/min).\n"
            "3. 'save_user_preference' (Save Tool): CHỈ dùng tool này khi người dùng BÀY TỎ SỞ THÍCH (ví dụ: 'tôi thích...', 'tác giả yêu thích của tôi là...').\n"
            "4. 'get_personalized_recommendation' (Rec Tool): CHỈ dùng tool này khi người dùng hỏi GỢI Ý CHUNG CHUNG (ví dụ: 'gợi ý sách cho tôi', 'tìm sách hay đi').\n"
            "**KHÔNG** dùng tool này khi người dùng chỉ đang LƯU SỞ THÍCH.\n"
            
            "QUY TẮC QUAN TRỌNG NHẤT:\n"
            "Nếu một câu hỏi phức tạp (ví dụ: 'tóm tắt cuốn sách đắt nhất...'), "
            "bạn PHẢI dùng 'sql_tool' để tìm sách trước, sau đó dùng 'smart_book_retriever' để tóm tắt."
        )),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# tạo Agent 
def create_book_agent_executor():
    """
    Hàm này sẽ lắp ráp và trả về Agent Executor hoàn chỉnh.
    """
    print("[AgentFactory] Đang tạo Agent Executor...")
    
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0) # Dùng model từ config
    
    print("[AgentFactory] Đang khởi tạo RAG, SQL...")
    smart_rag_engine = SmartRetriever(device='cpu') # RAG
    db = SQLDatabase.from_uri(f"sqlite:///{SQL_DB_PATH}") # SQL
    
    print("[AgentFactory] Đang khởi tạo 4 Tools...")
    rag_tool = SmartRAGTool(rag_engine=smart_rag_engine)
    
    sql_tool = QuerySQLDatabaseTool(db=db, llm=llm)
    sql_tool.description = ( 
        "Rất hữu ích khi bạn cần trả lời các câu hỏi về dữ liệu CÓ CẤU TRÚC (structured data) "
        "như giá (price), xếp hạng (rating), số trang (page_count), năm xuất bản (publication_year), "
        "hoặc để đếm (count), tính trung bình (average), tìm giá trị lớn nhất (max)/nhỏ nhất (min). "
        "KHÔNG dùng tool này để hỏi về mô tả sách, nội dung, hay tiểu sử tác giả."
    )
    
    save_pref_tool = SavePreferenceTool()
    get_rec_tool = GetPersonalizedRecommendationTool(rag_tool=rag_tool) # Tool gọi tool
    
    tools = [rag_tool, sql_tool, save_pref_tool, get_rec_tool]
    
    # khởi tạo memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # lắp agent
    print("[AgentFactory] Đang lắp ráp Agent...")
    agent = create_openai_tools_agent(llm, tools, AGENT_PROMPT)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory, 
        verbose=True
    )
    
    print("[AgentFactory] Agent Executor đã được tạo thành công.")
    return agent_executor

# 'if __name__ == "__main__":' ở đây để test,
