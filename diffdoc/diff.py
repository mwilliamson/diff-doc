import difflib
import subprocess
import tempfile


def generate_diff(old, new):
    diff = tuple(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
    ))
    assert diff[0].startswith("---")
    assert diff[1].startswith("+++")
    return "---\n+++\n" + "".join(diff[2:])


def apply_patch(old, patch):
    with tempfile.NamedTemporaryFile("w+t") as content_fileobj:
        content_fileobj.write(old)
        content_fileobj.flush()

        with tempfile.NamedTemporaryFile("w+t") as patch_fileobj:
            patch_fileobj.write(patch)
            patch_fileobj.flush()

            subprocess.run(["patch", content_fileobj.name, patch_fileobj.name, "--quiet"], check=True)

        with open(content_fileobj.name, "rt") as new_content_fileobj:
            return new_content_fileobj.read()
