import re
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")


def fake_cccd() -> str:
    return str(fake.random_number(digits=12, fix_len=True))


def fake_phone() -> str:
    prefix = fake.random_element(elements=("03", "05", "07", "08", "09"))
    return prefix + fake.numerify("########")


def fake_safe_email() -> str:
    suffix = fake.uuid4().replace("-", "")
    return f"user_{suffix}@anon.medviet.local"


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", str(value))


def is_email(value: str) -> bool:
    return re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        str(value)
    ) is not None


def is_cccd(value: str) -> bool:
    digits = digits_only(value)

    # Raw CCCD is 12 digits. pandas may remove leading zero, so allow 11 or 12.
    return len(digits) in (11, 12)


def is_vn_phone(value: str) -> bool:
    digits = digits_only(value)

    # Normal string: 0912345678
    if re.fullmatch(r"0[35789]\d{8}", digits):
        return True

    # pandas may remove leading zero: 0912345678 -> 912345678
    if re.fullmatch(r"[35789]\d{8}", digits):
        return True

    return False


class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        text = str(text)
        results = detect_pii(text, self.analyzer)

        if not results:
            return text

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": fake_safe_email()}),
                "VN_CCCD": OperatorConfig("replace", {"new_value": fake_cccd()}),
                "VN_PHONE": OperatorConfig("replace", {"new_value": fake_phone()}),
            }
        elif strategy == "mask":
            operators = {
                "PERSON": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8, "from_end": False}),
                "EMAIL_ADDRESS": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 6, "from_end": False}),
                "VN_CCCD": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8, "from_end": False}),
                "VN_PHONE": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 6, "from_end": False}),
            }
        elif strategy == "hash":
            operators = {
                "PERSON": OperatorConfig("hash", {"hash_type": "sha256"}),
                "EMAIL_ADDRESS": OperatorConfig("hash", {"hash_type": "sha256"}),
                "VN_CCCD": OperatorConfig("hash", {"hash_type": "sha256"}),
                "VN_PHONE": OperatorConfig("hash", {"hash_type": "sha256"}),
            }
        else:
            raise ValueError(f"Unsupported anonymization strategy: {strategy}")

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )

        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        if "ho_ten" in df_anon.columns:
            df_anon["ho_ten"] = [fake.name() for _ in range(len(df_anon))]

        if "cccd" in df_anon.columns:
            df_anon["cccd"] = [fake_cccd() for _ in range(len(df_anon))]

        if "ngay_sinh" in df_anon.columns:
            df_anon["ngay_sinh"] = df_anon["ngay_sinh"].astype(str).apply(
                lambda x: x[-4:] if len(x) >= 4 else "UNKNOWN"
            )

        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [fake_phone() for _ in range(len(df_anon))]

        if "email" in df_anon.columns:
            df_anon["email"] = [fake_safe_email() for _ in range(len(df_anon))]

        if "dia_chi" in df_anon.columns:
            df_anon["dia_chi"] = [fake.address() for _ in range(len(df_anon))]

        if "bac_si_phu_trach" in df_anon.columns:
            df_anon["bac_si_phu_trach"] = [fake.name() for _ in range(len(df_anon))]

        return df_anon

    def calculate_detection_rate(self, original_df: pd.DataFrame, pii_columns: list) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            if col not in original_df.columns:
                continue

            for value in original_df[col].astype(str):
                total += 1
                value_str = str(value)

                if col == "cccd":
                    if is_cccd(value_str):
                        detected += 1
                    continue

                if col == "so_dien_thoai":
                    if is_vn_phone(value_str):
                        detected += 1
                    continue

                if col == "email":
                    if is_email(value_str):
                        detected += 1
                    continue

                results = detect_pii(value_str, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
