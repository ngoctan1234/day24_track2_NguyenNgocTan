# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """
    Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN.
    Detect:
    - VN_CCCD: CCCD Việt Nam gồm đúng 12 chữ số
    - VN_PHONE: số điện thoại di động Việt Nam
    - EMAIL_ADDRESS: email
    - PERSON: tên người
    """

    # CCCD VN: đúng 12 chữ số
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{12}\b",
        score=0.9
    )

    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd", "can cuoc", "chung minh"],
        supported_language="vi"
    )

    # Số điện thoại VN: 0[3|5|7|8|9]xxxxxxxx
    phone_pattern = Pattern(
        name="vn_phone",
        regex=r"\b0[35789]\d{8}\b",
        score=0.85
    )

    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[phone_pattern],
        context=["điện thoại", "sdt", "phone", "liên hệ", "dien thoai", "lien he"],
        supported_language="vi"
    )

    # Dùng model đa ngôn ngữ cho spaCy
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [
            {
                "lang_code": "vi",
                "model_name": "xx_ent_wiki_sm"
            }
        ]
    })

    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["vi"]
    )

    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    Detect PII trong text tiếng Việt.
    Entities cần detect:
    - PERSON
    - EMAIL_ADDRESS
    - VN_CCCD
    - VN_PHONE
    """
    results = analyzer.analyze(
        text=str(text),
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results