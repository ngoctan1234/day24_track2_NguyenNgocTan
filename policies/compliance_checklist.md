# MedViet AI Governance Compliance Checklist

## 1. Data Protection

- [x] Raw patient data is stored separately in `data/raw/`.
- [x] Raw PII data is excluded from submission using `.gitignore`.
- [x] Anonymized data is generated in `data/processed/patients_anonymized.csv`.
- [x] PII columns are identified and processed:
  - ho_ten
  - cccd
  - ngay_sinh
  - so_dien_thoai
  - email
  - dia_chi
  - bac_si_phu_trach

## 2. PII Detection

- [x] Custom recognizer for Vietnamese CCCD.
- [x] Custom recognizer for Vietnamese phone numbers.
- [x] Email detection supported.
- [x] Detection rate test passes with pytest.
- [x] PII tests passed: `6 passed`.

## 3. Anonymization

- [x] Patient names are replaced with fake names.
- [x] CCCD values are replaced with fake CCCD values.
- [x] Phone numbers are replaced with fake phone numbers.
- [x] Emails are replaced with safe fake emails.
- [x] Date of birth is generalized to year only.
- [x] Disease and lab result columns are preserved for model training.

## 4. Access Control

- [x] RBAC implemented using Casbin.
- [x] FastAPI endpoints are protected by role-based permissions.
- [x] Admin can access raw patient data.
- [x] ML engineer cannot access raw patient data.
- [x] ML engineer can access anonymized training data.
- [x] Data analyst can access aggregated metrics.
- [x] Unauthorized actions return 403.

## 5. Encryption

- [x] Envelope encryption implemented.
- [x] AES-256-GCM used for encryption.
- [x] KEK encrypts DEK.
- [x] DEK encrypts data.
- [x] Encryption round-trip test passed.
- [x] `.vault_key` excluded from submission.

## 6. Data Quality

- [x] Required columns validated.
- [x] Null values checked.
- [x] Duplicate patient IDs checked.
- [x] Email, CCCD, phone formats validated.
- [x] Disease categories validated.
- [x] Row count consistency checked.
- [x] Data quality report generated.

## 7. Security Audit

- [x] Bandit security scan completed.
- [x] Bandit JSON report generated.
- [x] Security scan summary generated.
- [x] Raw PII and vault key excluded from submission.

## 8. Reports

Generated reports:

- `reports/test_results.txt`
- `reports/rbac_summary.txt`
- `reports/rbac_bob_raw_403.txt`
- `reports/rbac_bob_anonymized.txt`
- `reports/rbac_carol_metrics.txt`
- `reports/rbac_bob_delete_403.txt`
- `reports/rbac_alice_delete.txt`
- `reports/encryption_test.txt`
- `reports/data_quality_report.json`
- `reports/bandit_report.json`
- `reports/security_scan_summary.txt`

## Final Notes

This project demonstrates a local AI data governance pipeline for healthcare data, including PII detection, anonymization, role-based access control, encryption, data quality validation, and security scanning.
