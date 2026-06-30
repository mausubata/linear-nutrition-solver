import numpy as np

def optimize_ingredients(ingredients: list[dict], target: dict) -> dict:
    """
    線形代数（最小二乗法）を用いて、目標栄養素を満たす最適な食材の分量を算出する。
    
    :param ingredients: データベースから取得した食材データ（100gあたりの栄養素）のリスト
    :param target: 目標とする栄養素（タンパク質、脂質、炭水化物）の辞書
    :return: 各食材の推奨グラム数
    """
    if not ingredients:
        return {}

    names = [item["name"] for item in ingredients]

    # 行列Aの構築: 各列が1つの食材、各行が栄養素（タンパク質、脂質、炭水化物）となるようにする
    matrix = []
    for item in ingredients:
        matrix.append([item["protein"], item["fat"], item["carbo"]])
    
    # リストをNumPy配列に変換し、転置 (.T) することで (3 x 食材数) の行列 A を生成
    A = np.array(matrix).T 
    
    # ベクトルbの構築: 目標栄養素の (3 x 1) ベクトル
    b = np.array([target["protein"], target["fat"], target["carbo"]])

    # 最小二乗法により連立一次方程式 Ax = b の最適解ベクトル x を算出
    # rcond=None はNumPyの警告を防ぐための標準的な設定
    x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

    # 算出された解 x は「100g単位の倍率」を意味する。
    # 実空間での食事量として負の値は物理的に存在し得ないため、0未満は0に補正する。
    optimized_weights = {}
    for name, weight in zip(names, x):
        # 100を掛けて実際のグラム数に変換し、小数点第1位で丸める
        actual_gram = max(0.0, round(float(weight) * 100, 1))
        optimized_weights[name] = actual_gram

    return optimized_weights