import pandas as pd
import os
import time
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("FILE_PATH", "D:\\project\\sanxia_4144\\static")

def upload_file(file) -> dict:
    file_name = f"{time.strftime('%Y%m%d%H%M%S', time.localtime())}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, file_name)
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    df = _read_file(file_path)
    missing_info = _get_missing_info(df)
    preview = df.head(10).fillna("").to_dict(orient="records")
    columns = df.columns.tolist()

    return {
        "file_name": file_name,
        "file_path": file_path,
        "rows": len(df),
        "columns": len(columns),
        "column_names": columns,
        "missing_info": missing_info,
        "preview": preview,
    }


def process_missing(file_name: str, strategy: str, columns: list = None) -> dict:
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}

    df = _read_file(file_path)
    missing_before = df.isnull().sum().to_dict()

    target_cols = columns if columns else df.columns.tolist()

    if strategy == "drop":
        df = df.dropna(subset=target_cols)
    elif strategy == "mean":
        for col in target_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
    elif strategy == "median":
        for col in target_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
    elif strategy == "mode":
        for col in target_cols:
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val.iloc[0])
    elif strategy == "ffill":
        df[target_cols] = df[target_cols].ffill()
    elif strategy == "interpolate":
        for col in target_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].interpolate()

    missing_after = df.isnull().sum().to_dict()
    result_file = file_name.replace(".", "_cleaned.")
    result_path = os.path.join(UPLOAD_DIR, result_file)

    if result_file.endswith(".csv"):
        df.to_csv(result_path, index=False, encoding="utf-8-sig")
    else:
        df.to_excel(result_path, index=False)

    preview = df.head(10).fillna("").to_dict(orient="records")

    return {
        "file_name": result_file,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_before": missing_before,
        "missing_after": missing_after,
        "preview": preview,
        "download_url": f"http://localhost:8080/static/{result_file}",
    }


def get_full_data(file_name: str) -> dict:
    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        return {"error": "文件不存在"}

    df = _read_file(file_path)
    missing_info = _get_missing_info(df)
    data = df.fillna("").to_dict(orient="records")
    columns = df.columns.tolist()

    return {
        "columns": columns,
        "data": data,
        "rows": len(data),
        "missing_info": missing_info,
    }


def _read_file(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(file_path, encoding="utf-8-sig")
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")


def _get_missing_info(df: pd.DataFrame) -> list:
    total = len(df)
    result = []
    for col in df.columns:
        missing = int(df[col].isnull().sum())
        result.append({
            "column": col,
            "missing": missing,
            "total": total,
            "ratio": round(missing / total * 100, 2) if total > 0 else 0,
        })
    return result
