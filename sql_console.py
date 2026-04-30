from src.data.data_loader import DataLoader
from src.query.query_engine import QueryEngine

loader = DataLoader("data/raw")
loader.load_all()

print("🔵 SQL Console Ready. Type 'exit' to quit.")

while True:
    sql = input("SQL> ")

    if sql.lower() in ["exit", "quit"]:
        break

    try:
        result = QueryEngine.query(sql)
        print(result)
    except Exception as e:
        print("❌ Error:", e)
