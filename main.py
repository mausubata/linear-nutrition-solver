from fastapi import FastAPI, HTTPException
from database import get_connection
from models import OptimizeRequest, OptimizeResponse
from calculator import optimize_ingredients
import json

# FastAPIアプリケーションの初期化
app = FastAPI(title="Nutrition Optimization API")

@app.get("/ingredients")
def get_ingredients():
    """① データベースに登録されている食材一覧を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredients")
    rows = cursor.fetchall()
    conn.close()
    
    # SQLiteのRowオブジェクトを辞書のリストに変換して返す
    return [dict(row) for row in rows]

@app.post("/optimize", response_model=OptimizeResponse)
def optimize_diet(request: OptimizeRequest):
    """② 目標栄養素を満たす最適な食材の分量を計算し、履歴を保存する"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 食材データの取得
    cursor.execute("SELECT * FROM ingredients")
    rows = cursor.fetchall()
    if not rows:
        conn.close()
        raise HTTPException(status_code=500, detail="食材データが登録されていません。")
        
    ingredients_data = [dict(row) for row in rows]
    
    # 目標栄養素を辞書に変換
    target = {
        "protein": request.target_protein,
        "fat": request.target_fat,
        "carbo": request.target_carbo
    }
    
    # 線形代数を用いた計算ロジックの実行
    try:
        optimized_weights = optimize_ingredients(ingredients_data, target)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"計算中にエラーが発生しました: {str(e)}")
        
    # 計算結果から実際の総栄養素を検算する
    calculated_nutrients = {"protein": 0.0, "fat": 0.0, "carbo": 0.0, "total_kcal": 0.0}
    for item in ingredients_data:
        name = item["name"]
        if name in optimized_weights:
            # 100gあたりの栄養素なので比率を掛ける
            ratio = optimized_weights[name] / 100.0
            calculated_nutrients["protein"] += item["protein"] * ratio
            calculated_nutrients["fat"] += item["fat"] * ratio
            calculated_nutrients["carbo"] += item["carbo"] * ratio
            calculated_nutrients["total_kcal"] += item["kcal"] * ratio
            
    # 小数点第1位で丸める
    for key in calculated_nutrients:
        calculated_nutrients[key] = round(calculated_nutrients[key], 1)
        
    # 計算履歴をJSON文字列としてデータベースに保存
    result_json = json.dumps({
        "weights": optimized_weights,
        "nutrients": calculated_nutrients
    })
    
    cursor.execute("""
        INSERT INTO history (target_protein, target_fat, target_carbo, calculated_result)
        VALUES (?, ?, ?, ?)
    """, (request.target_protein, request.target_fat, request.target_carbo, result_json))
    
    conn.commit()
    conn.close()
    
    return OptimizeResponse(
        optimized_weights=optimized_weights,
        calculated_nutrients=calculated_nutrients
    )

@app.get("/history")
def get_history():
    """③ 過去の最適化計算の履歴を取得する"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history ORDER BY created_at DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    
    history_list = []
    for row in rows:
        data = dict(row)
        # データベースに保存されているJSON文字列を辞書に戻す
        data["calculated_result"] = json.loads(data["calculated_result"])
        history_list.append(data)
        
    return history_list