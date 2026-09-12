import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("release", Path(__file__).with_name("build-release.py"))
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseContractTests(unittest.TestCase):
    def test_exact_asset_bytes_and_rejected_inputs(self):
        fork = json.loads((release.ROOT / "retrom-fork.json").read_text())
        tag = "retrom-core-g05a05e931b39-r1"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            for name in set(fork["releaseAssets"]) - {"rpg-runtime-release.json"}:
                (output / name).write_bytes(b"fixture")
            (output / "LICENSE").write_bytes((release.ROOT / "LICENSE").read_bytes())
            (output / "gbe-pokemini.wasm").write_bytes(b"\0asm\x01\0\0\0")
            metadata = release.describe(output, fork, tag, "a" * 40)
            self.assertEqual(len(metadata["files"]), 4)
            self.assertTrue(all(item["sizeBytes"] > 0 and len(item["sha256"]) == 64 for item in metadata["files"]))
            with self.assertRaisesRegex(ValueError, "TAG_INVALID"):
                release.describe(output, fork, "latest", "a" * 40)
            (output / "extra.min").write_bytes(b"unlisted")
            with self.assertRaisesRegex(ValueError, "ASSETS_INVALID"):
                release.describe(output, fork, tag, "a" * 40)
            (output / "extra.min").unlink()
            (output / "LICENSE").write_bytes(b"modified")
            with self.assertRaisesRegex(ValueError, "LICENSE_INVALID"):
                release.describe(output, fork, tag, "a" * 40)


if __name__ == "__main__":
    unittest.main()
