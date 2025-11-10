import sqlite3
import config

class SQLDatabase:
    def __init__(self):
        print(f"[SQLDatabase] Đang kết nối tới: {config.SQL_DB_PATH}")
        try:
            self.conn = sqlite3.connect(config.SQL_DB_PATH)
            self.conn.row_factory = sqlite3.Row
            print("[SQLDatabase] Kết nối thành công.")
        except Exception as e:
            print(f"[SQLDatabase] Lỗi kết nối: {e}")
            self.conn = None

    def get_details_by_ids(self, unique_ids):
        """
        Truy vấn SQL DB để lấy thông tin chi tiết của sách từ list unique_id.
        """
        if not self.conn or not unique_ids:
            return []
            
        try:
            placeholders = ', '.join('?' for _ in unique_ids)
            query_sql = f"SELECT * FROM books WHERE unique_id IN ({placeholders})"
            
            cursor = self.conn.cursor()
            cursor.execute(query_sql, unique_ids)
            
            results = [dict(row) for row in cursor.fetchall()]
            
            # Sắp xếp lại kết quả theo đúng thứ tự của unique_ids
            results_sorted = sorted(results, key=lambda x: unique_ids.index(x['unique_id']))
            return results_sorted
        except Exception as e:
            print(f"[SQLDatabase] Lỗi truy vấn: {e}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()
            print("[SQLDatabase] Đã đóng kết nối.")