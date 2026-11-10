"""Fetch a consistent, verified snapshot of the public member skill. No stale fallback."""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from urllib.request import Request, urlopen
import zipfile

REPOSITORY = "hallelujah097hallelujah-design/yamaken-seo-contents-member"
MAX_BYTES = 10 * 1024 * 1024


def download(url):
    request = Request(url, headers={"User-Agent": "yamaken-seo-contents-member-loader/1", "Accept": "application/vnd.github+json"})
    with urlopen(request, timeout=40) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Download exceeds size limit")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=".yamaken-member-current")
    args = parser.parse_args()
    destination = Path(args.output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    staging = None
    try:
        commit = json.loads(download(f"https://api.github.com/repos/{REPOSITORY}/commits/main"))["sha"]
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError("Invalid commit SHA")
        archive = download(f"https://codeload.github.com/{REPOSITORY}/zip/{commit}")
        prefix = f"yamaken-seo-contents-member-{commit}/"
        staging = Path(tempfile.mkdtemp(prefix="snapshot-", dir=destination))
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            paths = set()
            total = 0
            for info in bundle.infolist():
                if info.is_dir():
                    continue
                if not info.filename.startswith(prefix):
                    raise ValueError("Unexpected archive root")
                name = info.filename[len(prefix):]
                path = PurePosixPath(name)
                if path.is_absolute() or ".." in path.parts or "\\" in name or name in paths or str(path) != name:
                    raise ValueError("Unsafe or duplicate manifest path")
                if not (name == "SKILL.md" or path.parts[0] in {"references", "scripts", "assets", "agents"}):
                    continue
                paths.add(name)
                total += info.file_size
                if total > MAX_BYTES:
                    raise ValueError("Extracted content exceeds size limit")
                data = bundle.read(info)
                output = staging.joinpath(*path.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(data)
            if "SKILL.md" not in paths or not any(p.startswith("references/") for p in paths) or not any(p.startswith("scripts/") for p in paths):
                raise ValueError("Incomplete skill snapshot")
        skill_text = (staging / "SKILL.md").read_text()
        if not re.search(r"^name: yamaken-seo-contents-member$", skill_text, re.M):
            raise ValueError("Unexpected skill name")
        version_match = re.search(r"バージョン：\*\*([^*]+)\*\*", skill_text)
        version = version_match.group(1) if version_match else "unknown"
        (staging / "source.json").write_text(json.dumps({"repository": REPOSITORY, "commit": commit, "version": version}, ensure_ascii=False))
        print(json.dumps({"ok": True, "skill_dir": str(staging), "commit": commit, "version": version, "file_count": len(paths)}, ensure_ascii=False))
        return 0
    except Exception as error:
        if staging is not None:
            shutil.rmtree(staging)
        print(json.dumps({"ok": False, "error": f"{type(error).__name__}: {error}", "action": "Use the GitHub connector to obtain the same-commit tree and files, or stop and report that latest rules could not be loaded. Do not use an old snapshot."}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
