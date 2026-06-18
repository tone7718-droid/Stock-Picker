from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapters"
INDEX = ROOT / "book" / "index.html"
VERCEL = ROOT / "vercel.json"

EXPECTED_FILES = [
    "01-서론.md",
    "02-기본개념.md",
    "03-PER.md",
    "04-PBR.md",
    "05-PSR.md",
    "06-EV-EBITDA.md",
    "07-조합하기.md",
    "08-실전예시.md",
    "09-함정.md",
    "10-체크리스트.md",
    "11-재무제표-초보자.md",
    "12-정성적-분석.md",
    "13-위험관리와-포지션.md",
    "14-매수와-매도.md",
    "15-심리적-실수.md",
    "16-투자-원칙.md",
]

FORBIDDEN_PATTERNS = {
    "월이익을 PER로 직접 나누는 옛 계산": r"3,000만\s*÷\s*100만",
    "월매출을 PSR로 직접 나누는 옛 계산": r"1억\s*/\s*500만",
    "잘못된 EPS 2,000원": r"주당순이익\s*=\s*2,000원",
    "잘못된 PSR 1.6배": r"PSR\s*=.*\*\*1\.6배\*\*",
    "PER 10배를 10개월로 표현": r"PER\s*10배.*10개월",
}


def fail(message: str) -> None:
    raise SystemExit(f"검증 실패: {message}")


def main() -> None:
    missing = [name for name in EXPECTED_FILES if not (CHAPTERS / name).is_file()]
    if missing:
        fail(f"누락된 챕터: {', '.join(missing)}")

    combined = "\n".join((CHAPTERS / name).read_text(encoding="utf-8") for name in EXPECTED_FILES)
    for label, pattern in FORBIDDEN_PATTERNS.items():
        if re.search(pattern, combined, flags=re.IGNORECASE | re.DOTALL):
            fail(label)

    per = (CHAPTERS / "03-PER.md").read_text(encoding="utf-8")
    example = (CHAPTERS / "08-실전예시.md").read_text(encoding="utf-8")
    required_facts = {
        "PER 예시 2.5배": "2.5배" in per,
        "실전 예시 PER 75배": "75배" in example,
        "실전 예시 PSR 16배": "16배" in example,
        "교육 목적 고지": "교육 목적" in combined,
    }
    failed = [label for label, ok in required_facts.items() if not ok]
    if failed:
        fail(f"필수 내용 누락: {', '.join(failed)}")

    index_text = INDEX.read_text(encoding="utf-8")
    unreferenced = [name for name in EXPECTED_FILES if name not in index_text]
    if unreferenced:
        fail(f"뷰어에서 참조되지 않는 챕터: {', '.join(unreferenced)}")

    config = json.loads(VERCEL.read_text(encoding="utf-8"))
    build_command = config.get("buildCommand", "")
    if "cp -R chapters book/chapters" not in build_command:
        fail("Vercel 배포 시 원본 챕터 동기화 명령이 없습니다")
    if config.get("outputDirectory") != "book":
        fail("Vercel outputDirectory가 book이 아닙니다")

    print("검증 성공: 16개 챕터, 핵심 산식, 뷰어 참조, 배포 설정이 정상입니다.")


if __name__ == "__main__":
    main()
