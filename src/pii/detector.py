from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
    RecognizerRegistry,
)
from presidio_analyzer.nlp_engine import NlpEngineProvider


def build_vietnamese_analyzer() -> AnalyzerEngine:
    # 1. CCCD VN: đúng 12 chữ số
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[
            Pattern(
                name="cccd_pattern",
                regex=r"\b\d{12}\b",
                score=0.9,
            )
        ],
        context=["cccd", "cmnd", "can cuoc", "căn cước", "chung minh", "chứng minh"],
        supported_language="vi",
    )

    # 2. Số điện thoại VN: 0[3|5|7|8|9]xxxxxxxx
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[
            Pattern(
                name="vn_phone",
                regex=r"\b0[35789]\d{8}\b",
                score=0.85,
            )
        ],
        context=["sdt", "phone", "dien thoai", "điện thoại", "lien he", "liên hệ"],
        supported_language="vi",
    )

    # 3. Email recognizer tự viết để chắc chắn detect được email trong tiếng Việt
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        patterns=[
            Pattern(
                name="email_pattern",
                regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                score=0.95,
            )
        ],
        context=["email", "mail"],
        supported_language="vi",
    )

    # 4. NLP engine spaCy
    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [
                {
                    "lang_code": "vi",
                    "model_name": "xx_ent_wiki_sm",
                }
            ],
        }
    )
    nlp_engine = provider.create_engine()

    # 5. Tạo registry riêng cho tiếng Việt
    registry = RecognizerRegistry(supported_languages=["vi"])

    # Thêm recognizer tự viết
    registry.add_recognizer(cccd_recognizer)
    registry.add_recognizer(phone_recognizer)
    registry.add_recognizer(email_recognizer)

    # Thêm predefined recognizers nếu Presidio hỗ trợ
    try:
        registry.load_predefined_recognizers(
            nlp_engine=nlp_engine,
            languages=["vi"],
        )
    except Exception:
        pass

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        registry=registry,
        supported_languages=["vi"],
    )

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    results = analyzer.analyze(
        text=str(text),
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
    return results
