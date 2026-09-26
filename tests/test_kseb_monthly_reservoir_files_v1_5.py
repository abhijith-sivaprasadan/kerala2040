from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_kseb_monthly_reservoir_files_v1_5.py"
SPEC = spec_from_file_location("audit_kseb_monthly_reservoir_files_v1_5", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot import audit module from {SCRIPT}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_inventory_is_continuous_fy2024_25():
    data = MODULE.load_inventory(MODULE.DEFAULT_INVENTORY)
    assert len(data["months"]) == 12
    assert data["months"][0]["month"] == "2024-04"
    assert data["months"][-1]["month"] == "2025-03"


@pytest.mark.parametrize(
    ("payload", "family"),
    [
        (b"%PDF-1.7\n", "pdf"),
        (bytes.fromhex("D0CF11E0A1B11AE1") + b"rest", "ole_compound"),
        (b"a,b\n1,2\n", "csv"),
        (b"a\tb\n1\t2\n", "tsv"),
        (b"plain text\nsecond line\n", "text"),
        (b"\x00\x01\x02\x03", "unknown_binary"),
    ],
)
def test_magic_and_text_detection(tmp_path: Path, payload: bytes, family: str):
    path = tmp_path / "source.bin"
    path.write_bytes(payload)
    assert MODULE.detect_file_type(path)["family"] == family


def test_xlsx_container_detection(tmp_path: Path):
    path = tmp_path / "source.anything"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("xl/workbook.xml", "<workbook/>")
    assert MODULE.detect_file_type(path)["family"] == "xlsx"


def test_ods_container_detection(tmp_path: Path):
    path = tmp_path / "source.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "mimetype",
            "application/vnd.oasis.opendocument.spreadsheet",
        )
    assert MODULE.detect_file_type(path)["family"] == "ods"


def test_audit_binds_file_to_inventory_without_using_size_as_hash(tmp_path: Path):
    inventory = MODULE.load_inventory(MODULE.DEFAULT_INVENTORY)
    source = tmp_path / "mystery"
    source.write_bytes(b"%PDF-1.7\nexample")
    result = MODULE.audit_file("2024-04", source, inventory["months"][0])
    assert result["month"] == "2024-04"
    assert result["local_file"]["detected_type"]["family"] == "pdf"
    assert len(result["local_file"]["sha256"]) == 64
    assert result["listed_size_comparison"]["binding_check"] is False
