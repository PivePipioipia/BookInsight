from openai import OpenAI
import os
from config import LLM_MODEL

class OpenAIQueryExpander:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY không được tìm thấy")

        self.client = OpenAI(api_key=api_key)
        self.model = LLM_MODEL
        print(f"[QueryExpander] Đã khởi tạo với model: {self.model}")

    def expand_query(self, query, num_queries=4):
        """
        Dùng LLM (GPT) để tạo ra các biến thể của câu hỏi.
        """
        print(f"[QueryExpander] Đang mở rộng câu hỏi: '{query}'...")
        prompt = f"""
        You are a helpful assistant. Your task is to generate {num_queries} different search queries 
        that are semantically similar to the original query.
        The queries should be diverse and cover different aspects or phrasings of the original query.

        Original Query: {query}

        Please provide ONLY a Python list of the new queries, like this:
        ["query 1", "query 2", "query 3", "query 4"]
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            generated_queries_str = response.choices[0].message.content
            generated_queries = eval(generated_queries_str)
            all_queries = [query] + generated_queries

            print(f"-> [QueryExpander] Các câu hỏi đã mở rộng: {all_queries}")
            return all_queries

        except Exception as e:
            print(f"[QueryExpander] Lỗi khi gọi OpenAI: {e}")
            return [query]