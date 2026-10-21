"""
PharmaLeaf AI - Windows Executable Build Script
Bundles the PySide6 application, OpenCV, Tesseract data, and dependencies
into a standalone distribution with SHA256 integrity verification.
"""
import os
import sys
import shutil
import hashlib
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")


def compute_sha256(file_path: str) -> str:
    """Calculates SHA256 checksum for a binary file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def build():
    print("=" * 60)
    print(" [PharmaLeaf AI] Windows Executable Packaging Process ")
    print("=" * 60)

    # 1. Clean previous build artifacts
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            print(f"Cleaning existing directory: {d}")
            shutil.rmtree(d, ignore_errors=True)

    # 2. Prepare PyInstaller command
    # Add tessdata resource directory and samples
    tessdata_src = os.path.join(BASE_DIR, "resources", "tessdata")
    tessdata_arg = f"{tessdata_src};resources/tessdata"
    samples_src = os.path.join(BASE_DIR, "samples")
    samples_arg = f"{samples_src};samples"

    pyinstaller_cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name=PharmaLeaf-AI",
        f"--add-data={tessdata_arg}",
        f"--add-data={samples_arg}",
        "--hidden-import=PySide6.QtPrintSupport",
        "--hidden-import=arabic_reshaper",
        "--hidden-import=bidi.algorithm",
        "--hidden-import=docx",
        "--hidden-import=reportlab",
        "--hidden-import=pymupdf",
        "--hidden-import=PIL",
        "--hidden-import=cv2",
        "--hidden-import=pytesseract",
        os.path.join(BASE_DIR, "main.py")
    ]

    print("\nRunning PyInstaller command:")
    print(" ".join(pyinstaller_cmd))

    ret = subprocess.run(pyinstaller_cmd, cwd=BASE_DIR)
    if ret.returncode != 0:
        print("\nERROR: PyInstaller build failed with exit code:", ret.returncode)
        sys.exit(ret.returncode)

    # 3. Verify output executable
    exe_path = os.path.join(DIST_DIR, "PharmaLeaf-AI", "PharmaLeaf-AI.exe")
    if not os.path.exists(exe_path):
        print(f"\nERROR: Expected executable not found at: {exe_path}")
        sys.exit(1)

    # 4. Generate SHA256 checksum
    checksum = compute_sha256(exe_path)
    checksum_file = os.path.join(DIST_DIR, "PharmaLeaf-AI-checksums.txt")
    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write(f"SHA256 (PharmaLeaf-AI.exe):\n{checksum}\n")

    exe_size_mb = os.path.getsize(exe_path) / (1024 * 1024)

    print("\n" + "=" * 60)
    print(" ✓ BUILD SUCCEEDED!")
    print(f" Binary Path: {exe_path}")
    print(f" Binary Size: {exe_size_mb:.2f} MB")
    print(f" SHA256:      {checksum}")
    print(f" Checksum File: {checksum_file}")
    print("=" * 60)


if __name__ == "__main__":
    build()
