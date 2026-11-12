import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "client.py"
SPEC = importlib.util.spec_from_file_location("seedance_client", MODULE_PATH)
CLIENT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(CLIENT)


class SeedanceClientTest(unittest.TestCase):
    def test_validate_and_dry_run_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            img = tmp_dir / "ref.png"
            vid = tmp_dir / "clay.mp4"
            img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 32)
            vid.write_bytes(b"ftypmp42" + b"1" * 64)

            job = {
                "task": "unit-test-shot",
                "model": "doubao-seedance-2-5-260628",
                "ratio": "21:9",
                "resolution": "480p",
                "duration": 5,
                "content": [
                    {"type": "text", "text": "参考@video1中的运镜轨迹，质感参考@image1，生成写实麦田收割机"},
                    {"type": "image_url", "role": "reference_image", "asset": str(img)},
                    {"type": "video_url", "role": "reference_video", "asset": str(vid)},
                ],
            }
            payload, audit, warnings = CLIENT.build_payload_and_audit(job, tmp_dir, dry_run=True)
            self.assertEqual(payload["model"], "doubao-seedance-2-5-260628")
            self.assertEqual(payload["resolution"], "480p")
            self.assertEqual(len(audit), 2)
            self.assertEqual(warnings, [])
            self.assertTrue(payload["content"][1]["image_url"]["url"].startswith("<dry-run:ref.png"))
            self.assertTrue(payload["content"][2]["video_url"]["url"].startswith("<dry-run:clay.mp4"))

    def test_warnings_on_missing_reference_prompt_or_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            vid = tmp_dir / "clay.mp4"
            vid.write_bytes(b"mp4data")

            job = {
                "task": "warn-test",
                "model": "doubao-seedance-2-5-260628",
                "content": [
                    {"type": "text", "text": "严格编辑@video1，修改为红色机甲"},
                    {"type": "video_url", "asset": str(vid)},
                ],
            }
            _, _, warnings = CLIENT.build_payload_and_audit(job, tmp_dir, dry_run=True)
            self.assertGreaterEqual(len(warnings), 3)

    def test_extract_output_urls(self):
        hist_dict = {"content": {"video_url": "https://cdn.example/out.mp4", "last_frame_url": "https://cdn.example/end.png"}}
        self.assertEqual(
            CLIENT.extract_output_urls(hist_dict),
            {"video_url": "https://cdn.example/out.mp4", "last_frame_url": "https://cdn.example/end.png"},
        )

        hist_list = {"content": [{"type": "video_url", "video_url": {"url": "https://cdn.example/list.mp4"}}]}
        self.assertEqual(CLIENT.extract_output_urls(hist_list), {"video_url": "https://cdn.example/list.mp4"})

    def test_dotenv_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            env_file = tmp_dir / ".env"
            env_file.write_text('\ufeffARK_API_KEY="test-key-123"\nSEEDANCE_MODEL=doubao-seedance-2-0-260128\n', encoding="utf-8")
            old_root = CLIENT.REPO_ROOT
            try:
                CLIENT.REPO_ROOT = tmp_dir
                parsed = CLIENT.load_repo_dotenv()
                self.assertEqual(parsed["ARK_API_KEY"], "test-key-123")
                self.assertEqual(parsed["SEEDANCE_MODEL"], "doubao-seedance-2-0-260128")
            finally:
                CLIENT.REPO_ROOT = old_root


if __name__ == "__main__":
    unittest.main()
