import re
import json
import pandas as pd


VALID_CONDITIONS = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]


def validate_anonymized_data(filepath: str) -> dict:
    df = pd.read_csv(filepath)

    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    def fail(message: str):
        results["success"] = False
        results["failed_checks"].append(message)

    required_columns = [
        "patient_id",
        "ho_ten",
        "cccd",
        "ngay_sinh",
        "so_dien_thoai",
        "email",
        "dia_chi",
        "benh",
        "ket_qua_xet_nghiem",
        "bac_si_phu_trach",
        "ngay_kham",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        fail(f"Missing required columns: {missing_columns}")
        return results

    important_columns = [
        "patient_id",
        "ho_ten",
        "cccd",
        "ngay_sinh",
        "so_dien_thoai",
        "email",
        "benh",
        "ket_qua_xet_nghiem",
    ]

    for col in important_columns:
        if df[col].isnull().any():
            fail(f"Column '{col}' contains null values")

    if df["patient_id"].duplicated().any():
        fail("Duplicate patient_id found")

    # CCCD fake/anonymized vẫn phải có dạng số hợp lệ.
    # pandas có thể làm mất số 0 đầu, nên chấp nhận 11 hoặc 12 chữ số.
    cccd_digits = df["cccd"].astype(str).str.replace(r"\D", "", regex=True)
    if not cccd_digits.str.len().isin([11, 12]).all():
        fail("Invalid CCCD format found")

    # Phone VN: chấp nhận cả dạng có 0 đầu và mất 0 đầu do pandas.
    def valid_phone(value):
        digits = re.sub(r"\D", "", str(value))
        return bool(
            re.fullmatch(r"0[35789]\d{8}", digits)
            or re.fullmatch(r"[35789]\d{8}", digits)
        )

    if not df["so_dien_thoai"].apply(valid_phone).all():
        fail("Invalid Vietnamese phone format found")

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not df["email"].astype(str).str.match(email_pattern).all():
        fail("Invalid email format found")

    values = pd.to_numeric(df["ket_qua_xet_nghiem"], errors="coerce")
    if values.isnull().any():
        fail("ket_qua_xet_nghiem contains non-numeric values")
    elif not values.between(0, 50).all():
        fail("ket_qua_xet_nghiem out of range [0, 50]")

    if not df["benh"].isin(VALID_CONDITIONS).all():
        fail("Invalid disease category found in benh column")

    # Sau anonymization, ngay_sinh đã generalize thành năm sinh.
    if not df["ngay_sinh"].astype(str).str.match(r"^\d{4}$").all():
        fail("ngay_sinh is not generalized to year-only format")

    # Số dòng anonymized phải bằng raw.
    try:
        raw_df = pd.read_csv("data/raw/patients_raw.csv")
        if len(df) != len(raw_df):
            fail(f"Row count mismatch: anonymized={len(df)}, raw={len(raw_df)}")
    except FileNotFoundError:
        fail("Raw file not found for row count comparison")

    results["stats"]["failed_check_count"] = len(results["failed_checks"])
    results["stats"]["disease_counts"] = df["benh"].value_counts().to_dict()
    results["stats"]["duplicate_patient_id_count"] = int(df["patient_id"].duplicated().sum())
    results["stats"]["null_counts"] = df[important_columns].isnull().sum().to_dict()

    return results


if __name__ == "__main__":
    report = validate_anonymized_data("data/processed/patients_anonymized.csv")
    print(json.dumps(report, ensure_ascii=False, indent=2))
