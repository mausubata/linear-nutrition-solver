import sqlite3

DB_NAME = "nutrition.db"

def get_connection():
    """データベースへの接続を取得する"""
    conn = sqlite3.connect(DB_NAME)
    # 検索結果を辞書形式で取得できるように設定
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """テーブルの作成と初期データの投入を行う"""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. 食材マスタテーブルの作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            protein REAL NOT NULL,
            fat REAL NOT NULL,
            carbo REAL NOT NULL,
            kcal REAL NOT NULL
        )
    """)

    # 2. 計算履歴テーブルの作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_protein REAL NOT NULL,
            target_fat REAL NOT NULL,
            target_carbo REAL NOT NULL,
            calculated_result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 初期食材データの定義（100gあたりの栄養素: P, F, C, kcal）
    default_ingredients = [
        ("pork", 20.0, 15.0, 0.0, 220.0),
        ("rice", 2.5, 0.3, 37.1, 160.0),
        ("broccoli", 4.3, 0.5, 5.2, 33.0),
        ("spinach", 2.2, 0.4, 3.1, 20.0),
        ("egg", 12.3, 10.3, 0.3, 151.0),
        ("natto", 16.5, 10.0, 12.1, 200.0)
    ]

    # データの挿入（既に存在する場合はスキップ）
    for name, p, f, c, kcal in default_ingredients:
        try:
            cursor.execute("""
                INSERT INTO ingredients (name, protein, fat, carbo, kcal)
                VALUES (?, ?, ?, ?, ?)
            """, (name, p, f, c, kcal))
        except sqlite3.IntegrityError:
            # 既に食材が登録されている場合は何もしない
            pass

    conn.commit()
    conn.close()

# スクリプトが直接実行された場合にデータベースを初期化する
if __name__ == "__main__":
    init_db()