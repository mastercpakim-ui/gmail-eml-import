from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Iterable

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


DEFAULT_SOURCE_DIR = "."
DEFAULT_SAMPLE_LABEL = "Imported_Test/eml-import"
DEFAULT_FULL_LABEL = "Imported/eml-import"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CSV_ENCODING = "utf-8-sig"


@dataclass
class RunResult:
    exit_code: int
    message: str
    total_files: int = 0
    imported_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely import local EML files into Gmail with the Gmail API.")
    parser.add_argument("--mode", choices=["dry-run", "sample", "full"], default="dry-run")
    parser.add_argument("--source-dir", default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--label", default=None)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--method", choices=["import", "insert"], default="import")
    parser.add_argument("--confirm-full-import", action="store_true")
    parser.add_argument(
        "--repair-malformed-headers",
        action="store_true",
        help="Temporarily repair malformed header continuations before import. Original EML files are not changed.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_stdout()
    args = parse_args(argv)
    result = run(args, project_root=Path(__file__).resolve().parent)
    print(result.message)
    return result.exit_code


def configure_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run(args: argparse.Namespace, *, project_root: Path, gmail_service: Any | None = None) -> RunResult:
    project_root = project_root.resolve()
    logs_dir = project_root / "logs"
    state_dir = project_root / "state"
    logs_dir.mkdir(exist_ok=True)
    state_dir.mkdir(exist_ok=True)

    source_dir = normalize_path(args.source_dir)
    label = choose_label(args)

    if args.mode == "full" and not args.confirm_full_import:
        return RunResult(2, "refusing full import: pass --confirm-full-import only after manual Gmail verification")

    eml_files = find_eml_files(source_dir)
    if args.mode == "dry-run":
        return dry_run(eml_files, logs_dir)

    if gmail_service is None:
        gmail_service = build_gmail_service(project_root / "credentials.json", project_root / "token.json")

    manifest_path = state_dir / "imported_manifest.json"
    manifest = load_manifest(manifest_path)
    imported_hashes = set(manifest.get("imported", {}).keys())
    current_seen: set[str] = set()
    success_rows: list[dict[str, Any]] = []
    failed_rows: list[dict[str, Any]] = []
    skipped = 0
    imported = 0
    sample_remaining = None
    if args.mode == "sample":
        already_sample_imported = count_manifest_label(manifest, label)
        sample_remaining = max(args.limit - already_sample_imported, 0)
        candidates = eml_files
    else:
        candidates = eml_files
    label_id = ensure_label(gmail_service, label)

    for path in candidates:
        if sample_remaining is not None and imported >= sample_remaining:
            break
        sha256 = sha256_file(path)
        metadata = inspect_eml(path, sha256=sha256)
        if sha256 in imported_hashes or sha256 in current_seen:
            skipped += 1
            continue
        current_seen.add(sha256)
        raw_bytes = path.read_bytes()
        header_repaired = False
        date_source = "header" if metadata["date"] else ""
        if not metadata["date"] and args.repair_malformed_headers:
            repaired = repair_malformed_headers(raw_bytes)
            repaired_metadata = inspect_eml_bytes(repaired, path=path, sha256=sha256)
            if repaired_metadata["date"]:
                raw_bytes = repaired
                metadata = repaired_metadata
                header_repaired = True
                date_source = "received"

        if not metadata["date"]:
            failed_rows.append(failure_row(path, sha256, "missing Date header"))
            continue

        try:
            message_id = upload_message(
                gmail_service,
                path,
                label_id=label_id,
                method=args.method,
                raw_bytes=raw_bytes,
            )
        except Exception as exc:  # noqa: BLE001 - continue-on-failure migration tool.
            failed_rows.append(failure_row(path, sha256, f"{type(exc).__name__}: {exc}"))
            continue

        imported += 1
        manifest["imported"][sha256] = {
            "path": str(path),
            "gmail_message_id": message_id,
            "label": label,
            "method": args.method,
            "subject": metadata["subject"],
            "date": metadata["date"],
            "header_repaired": header_repaired,
            "date_source": date_source,
        }
        success_rows.append(
            {
                "path": str(path),
                "sha256": sha256,
                "gmail_message_id": message_id,
                "label": label,
                "method": args.method,
                "date": metadata["date"],
                "from": metadata["from"],
                "to": metadata["to"],
                "subject": metadata["subject"],
                "message_id": metadata["message_id"],
                "header_repaired": str(header_repaired).lower(),
                "date_source": date_source,
            }
        )
        save_manifest(manifest_path, manifest)

    append_csv(logs_dir / "import_log.csv", success_rows, IMPORT_LOG_FIELDS)
    append_csv(logs_dir / "failed.csv", failed_rows, FAILED_FIELDS)
    save_manifest(manifest_path, manifest)

    exit_code = 0 if imported > 0 and not failed_rows else 1 if failed_rows else 0
    return RunResult(
        exit_code,
        f"{args.mode} import finished: imported={imported}, skipped={skipped}, failed={len(failed_rows)}, label={label}",
        total_files=len(eml_files),
        imported_count=imported,
        skipped_count=skipped,
        failed_count=len(failed_rows),
    )


def count_manifest_label(manifest: dict[str, Any], label: str) -> int:
    return sum(1 for item in manifest.get("imported", {}).values() if item.get("label") == label)


def choose_label(args: argparse.Namespace) -> str:
    if args.label:
        return args.label
    if args.mode == "full":
        return DEFAULT_FULL_LABEL
    return DEFAULT_SAMPLE_LABEL


def normalize_path(path_text: str) -> Path:
    if os.name == "nt" and path_text.startswith("/mnt/") and len(path_text) > 6:
        drive = path_text[5]
        rest = path_text[6:].replace("/", "\\")
        return Path(f"{drive.upper()}:\\{rest}")
    return Path(path_text).expanduser()


def find_eml_files(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"source directory not found: {source_dir}")
    return sorted(path for path in source_dir.rglob("*.eml") if path.is_file())


def dry_run(eml_files: list[Path], logs_dir: Path) -> RunResult:
    rows = []
    for path in eml_files:
        sha256 = sha256_file(path)
        rows.append(inspect_eml(path, sha256=sha256))
    write_csv(logs_dir / "dry_run_report.csv", rows, DRY_RUN_FIELDS)
    write_duplicate_reports(rows, logs_dir)

    sample_lines = ["Proposed sample files:"]
    for path in eml_files[:10]:
        sample_lines.append(f"- {path}")
    message = "\n".join([f"dry-run found {len(eml_files)} .eml files", *sample_lines])
    return RunResult(0, message, total_files=len(eml_files))


def write_duplicate_reports(rows: list[dict[str, Any]], logs_dir: Path) -> None:
    sha_groups = duplicate_groups(rows, "sha256", include_blank=False)
    message_id_groups = duplicate_groups(rows, "message_id", include_blank=False)
    duplicate_rows = []

    for reason, groups in (("sha256", sha_groups), ("message_id", message_id_groups)):
        for group_index, group_rows in enumerate(groups, start=1):
            keeper = choose_duplicate_keeper(group_rows)
            for row in group_rows:
                duplicate_rows.append(
                    {
                        "duplicate_reason": reason,
                        "duplicate_group": group_index,
                        "duplicate_count": len(group_rows),
                        "is_keeper": str(row["path"] == keeper["path"]).lower(),
                        **{field: row.get(field, "") for field in DRY_RUN_FIELDS},
                    }
                )

    write_csv(logs_dir / "duplicate_report.csv", duplicate_rows, DUPLICATE_REPORT_FIELDS)
    summary = {
        "total_files": len(rows),
        "unique_sha256": len({row.get("sha256", "") for row in rows if row.get("sha256", "")}),
        "sha256_duplicate_groups": len(sha_groups),
        "sha256_duplicate_extra_files": sum(len(group) - 1 for group in sha_groups),
        "message_id_duplicate_groups": len(message_id_groups),
        "message_id_duplicate_extra_files": sum(len(group) - 1 for group in message_id_groups),
        "missing_message_id_files": sum(1 for row in rows if not row.get("message_id")),
    }
    (logs_dir / "duplicate_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def duplicate_groups(rows: list[dict[str, Any]], key: str, *, include_blank: bool) -> list[list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        value = str(row.get(key, "")).strip().lower()
        if not value and not include_blank:
            continue
        groups.setdefault(value, []).append(row)
    return [group for group in groups.values() if len(group) > 1]


def choose_duplicate_keeper(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(rows, key=lambda row: (len(str(row.get("path", ""))), str(row.get("path", "")).lower()))[0]


def inspect_eml(path: Path, *, sha256: str) -> dict[str, Any]:
    return inspect_eml_bytes(path.read_bytes(), path=path, sha256=sha256)


def inspect_eml_bytes(raw: bytes, *, path: Path, sha256: str) -> dict[str, Any]:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    return {
        "path": str(path),
        "sha256": sha256,
        "date": header_value(message["Date"]),
        "from": header_value(message["From"]),
        "to": header_value(message["To"]),
        "subject": header_value(message["Subject"]),
        "message_id": header_value(message["Message-ID"]),
        "has_attachments": str(has_attachments(message)).lower(),
        "size_bytes": len(raw),
    }


def header_value(value: Any) -> str:
    return "" if value is None else str(value)


def has_attachments(message: Any) -> bool:
    for part in message.walk():
        disposition = (part.get_content_disposition() or "").lower()
        filename = part.get_filename()
        if disposition == "attachment" or filename:
            return True
    return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_gmail_service(credentials_path: Path, token_path: Path) -> Any:
    if not credentials_path.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {credentials_path}. Create a Google Cloud Desktop OAuth client and place it there."
        )

    credentials = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            print("OAuth browser authorization is about to open. Confirm the account and Gmail access manually.")
            credentials = flow.run_local_server(port=0)
        token_path.write_text(credentials.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=credentials)


BROKEN_RECEIVED_CONTINUATION = re.compile(rb"(?m)^(Received:\s+from[^\r\n]*\r?\n)(by\s+\S+\s+with\s+)")


def repair_malformed_headers(raw: bytes) -> bytes:
    return BROKEN_RECEIVED_CONTINUATION.sub(rb"\1 \2", raw, count=1)


def ensure_label(service: Any, label_name: str) -> str:
    existing = service.users().labels().list(userId="me").execute().get("labels", [])
    for label in existing:
        if label.get("name") == label_name:
            return label["id"]

    created = (
        service.users()
        .labels()
        .create(
            userId="me",
            body={
                "name": label_name,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show",
            },
        )
        .execute()
    )
    return created["id"]


def upload_message(service: Any, path: Path, *, label_id: str, method: str, raw_bytes: bytes | None = None) -> str:
    raw = base64.urlsafe_b64encode(raw_bytes if raw_bytes is not None else path.read_bytes()).decode("ascii")
    body = {"raw": raw, "labelIds": [label_id]}
    messages = service.users().messages()
    if method == "import":
        response = messages.import_(
            userId="me",
            body=body,
            internalDateSource="dateHeader",
            neverMarkSpam=True,
        ).execute()
    else:
        response = messages.insert(
            userId="me",
            body=body,
            internalDateSource="dateHeader",
        ).execute()
    return response.get("id", "")


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"imported": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("imported", {})
    for item in data["imported"].values():
        item.setdefault("date_source", "header" if item.get("date") else "")
    return data


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding=CSV_ENCODING) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    ensure_csv_fields(path, fields)
    if not rows:
        if not path.exists():
            write_csv(path, [], fields)
        return
    exists = path.exists()
    with path.open("a", newline="", encoding=CSV_ENCODING) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def ensure_csv_fields(path: Path, fields: list[str]) -> None:
    if not path.exists():
        return
    with path.open(newline="", encoding=CSV_ENCODING) as handle:
        reader = csv.DictReader(handle)
        existing_fields = reader.fieldnames or []
        if existing_fields == fields:
            return
        existing_rows = list(reader)

    merged_fields = list(existing_fields)
    for field in fields:
        if field not in merged_fields:
            merged_fields.append(field)
    if merged_fields != fields:
        for field in merged_fields:
            if field not in fields:
                fields.append(field)

    normalized = [{field: row.get(field, "") for field in fields} for row in existing_rows]
    write_csv(path, normalized, fields)


def failure_row(path: Path, sha256: str, reason: str) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256, "reason": reason}


DRY_RUN_FIELDS = ["path", "sha256", "date", "from", "to", "subject", "message_id", "has_attachments", "size_bytes"]
DUPLICATE_REPORT_FIELDS = [
    "duplicate_reason",
    "duplicate_group",
    "duplicate_count",
    "is_keeper",
    *DRY_RUN_FIELDS,
]
IMPORT_LOG_FIELDS = [
    "path",
    "sha256",
    "gmail_message_id",
    "label",
    "method",
    "date",
    "from",
    "to",
    "subject",
    "message_id",
    "header_repaired",
    "date_source",
]
FAILED_FIELDS = ["path", "sha256", "reason"]


class FakeExecutable:
    def __init__(self, value: dict[str, Any]):
        self.value = value

    def execute(self) -> dict[str, Any]:
        return self.value


class FakeLabelResource:
    def __init__(self, service: "FakeGmailService"):
        self.service = service

    def list(self, userId: str) -> FakeExecutable:  # noqa: N803 - Google API parameter name.
        return FakeExecutable({"labels": [{"id": value, "name": key} for key, value in self.service.labels.items()]})

    def create(self, userId: str, body: dict[str, Any]) -> FakeExecutable:  # noqa: N803
        label_id = f"Label_{len(self.service.labels) + 1}"
        self.service.labels[body["name"]] = label_id
        return FakeExecutable({"id": label_id, "name": body["name"]})


class FakeMessageResource:
    def __init__(self, service: "FakeGmailService"):
        self.service = service

    def import_(self, **kwargs: Any) -> FakeExecutable:
        self.service.import_calls.append(kwargs)
        return FakeExecutable({"id": f"msg_{len(self.service.import_calls)}"})

    def insert(self, **kwargs: Any) -> FakeExecutable:
        self.service.insert_calls.append(kwargs)
        return FakeExecutable({"id": f"msg_{len(self.service.insert_calls)}"})


class FakeUserResource:
    def __init__(self, service: "FakeGmailService"):
        self.service = service

    def labels(self) -> FakeLabelResource:
        return FakeLabelResource(self.service)

    def messages(self) -> FakeMessageResource:
        return FakeMessageResource(self.service)


class FakeGmailService:
    def __init__(self) -> None:
        self.labels: dict[str, str] = {}
        self.import_calls: list[dict[str, Any]] = []
        self.insert_calls: list[dict[str, Any]] = []

    def users(self) -> FakeUserResource:
        return FakeUserResource(self)


if __name__ == "__main__":
    sys.exit(main())

