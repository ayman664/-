import os
import shutil
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app import app


def main():
    site_url = os.environ.get("SITE_URL", "").rstrip("/")
    site_prefix = os.environ.get("SITE_PREFIX", "").rstrip("/")
    if not site_url.startswith(("https://", "http://")):
        raise RuntimeError("SITE_URL must be an absolute HTTP or HTTPS URL.")
    if site_prefix and not site_prefix.startswith("/"):
        raise RuntimeError("SITE_PREFIX must start with '/'.")

    output_dir = BASE_DIR / "_site"
    output_dir.mkdir(exist_ok=True)
    app.config["STATIC_SITE_BUILD"] = True

    with app.test_client() as client:
        overrides = {"SCRIPT_NAME": site_prefix}
        for route, filename in (
            ("/", "index.html"),
            ("/robots.txt", "robots.txt"),
            ("/sitemap.xml", "sitemap.xml"),
        ):
            response = client.get(route, environ_overrides=overrides)
            if response.status_code != 200:
                raise RuntimeError(f"Static export failed for {route}: HTTP {response.status_code}")
            (output_dir / filename).write_bytes(response.data)

    shutil.copytree(BASE_DIR / "static", output_dir / "static", dirs_exist_ok=True)
    (output_dir / ".nojekyll").touch()


if __name__ == "__main__":
    main()
