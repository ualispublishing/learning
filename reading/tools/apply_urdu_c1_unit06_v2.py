from __future__ import annotations

import base64
import hashlib
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTS = [HERE / f"urdu_c1_u06_payload_{i:02d}.txt" for i in range(1, 7)]
payload = "".join(path.read_text(encoding="utf-8").strip() for path in PARTS)
if len(payload) != 25328:
    raise RuntimeError(f"Unit 6 payload length mismatch: {len(payload)} != 25328")
source = zlib.decompress(base64.b64decode(payload))
expected_sha256 = "9e6c6b394300e587b26a0e0e8c8487aa8e000f6f1dbaa343d8a2ee804cd7819c"
actual_sha256 = hashlib.sha256(source).hexdigest()
if actual_sha256 != expected_sha256:
    raise RuntimeError(f"Unit 6 source SHA-256 mismatch: {actual_sha256}")
exec(compile(source.decode("utf-8"), __file__, "exec"))
