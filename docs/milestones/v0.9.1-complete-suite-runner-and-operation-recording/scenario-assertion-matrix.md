# Scenario Assertion Matrix

Chinese mirror: `scenario-assertion-matrix.zh.md`.

Main scenario:

```text
complete-worldengine-validation-suite
```

The Chinese matrix is authoritative for detailed step-by-step assertions. It
maps Phase 1-4 step ids to UI operations, API evidence, required artifacts, and
PASS/BLOCKED assertions.

Global assertions:

- every executed step has an `operation-log.jsonl` entry;
- every API request has an `api-log.jsonl` entry;
- every downloaded artifact has an operation record and artifact ref;
- direct API harvest is not written to `operation-log.jsonl`;
- any redaction blocking marker forces FAIL.

