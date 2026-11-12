import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "openrouter_client.py"
SPEC = importlib.util.spec_from_file_location("openrouter_client", MODULE_PATH)
OR_CLIENT = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(OR_CLIENT)


class OpenRouterClientTest(unittest.TestCase):
    def test_validate_openrouter_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            img = tmp_dir / "ref.jpg"
            vid = tmp_dir / "clay.mp4"
            img.write_bytes(b"\xff\xd8\xff" + b"0" * 32)
            vid.write_bytes(b"ftypmp42" + b"1" * 64)

            job = {
                "task": "or-test-01",
                "model": "bytedance/seedance-2.5",
                "prompt": "Follow @video1 camera path strictly, match style of @image1.",
                "duration": 6,
                "resolution": "480p",
                "aspect_ratio": "21:9",
                "generate_audio": False,
                "input_references": [
                    {"type": "image_url", "asset": str(img)},
                    {"type": "video_url", "asset": str(vid)},
                ],
            }
            payload, audit, warnings = OR_CLIENT.build_openrouter_payload(job, tmp_dir, dry_run=True)
            self.assertEqual(payload["model"], "bytedance/seedance-2.5")
            self.assertEqual(payload["resolution"], "480p")
            self.assertEqual(payload["aspect_ratio"], "21:9")
            self.assertEqual(len(audit), 2)
            self.assertEqual(warnings, [])
            self.assertTrue(payload["input_references"][1]["video_url"]["url"].startswith("<dry-run:clay.mp4"))

            live_payload, _, _ = OR_CLIENT.build_openrouter_payload(job, tmp_dir, dry_run=False)
            self.assertTrue(live_payload["input_references"][0]["image_url"]["url"].startswith("data:image/jpeg;base64,"))
            self.assertTrue(live_payload["input_references"][1]["video_url"]["url"].startswith("data:video/mp4;base64,"))


if __name__ == "__main__":
    unittest.main()
