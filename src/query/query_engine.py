import duckdb
from src.data.registry import registry

class QueryEngine:

    @staticmethod
    def query(sql: str):
        con = duckdb.connect()

        # توجه: اینجا _tables استفاده می‌کنیم
        for name, df in registry._tables.items():
            con.register(name, df)

        return con.execute(sql).df()
