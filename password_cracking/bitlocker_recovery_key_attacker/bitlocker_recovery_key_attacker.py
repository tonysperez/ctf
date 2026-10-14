import subprocess
import tempfile
import os
import sys
import re

IMAGE = "/home/ctf/usb-image.img"
WORDLIST = "/home/ctf/usb-image-reco-wordlist.txt"


MOUNT_DIR = tempfile.mkdtemp()
DISLOCKER_OUT = os.path.join(MOUNT_DIR, "dislocker-file")


# ---------------------------
# Run shell command
# ---------------------------
def run(cmd, timeout=10):
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout
    )


# ---------------------------
# Clean + normalize candidate key
# ---------------------------
def normalize_key(raw: str) -> str:
    key = raw.strip().replace("\r", "").replace("\n", "")

    # remove common noise characters
    key = key.replace(" ", "")
    key = key.replace("s", "")   # removes stray '-s' artifacts if present in CTF dumps
    key = key.replace("S", "")

    # keep only digits and dashes
    key = re.sub(r"[^0-9\-]", "", key)

    return key


# ---------------------------
# Validate BitLocker structure + checksum rule
# ---------------------------
def is_valid_bitlocker_key(key: str) -> bool:
    parts = key.split("-")

    # Must be 8 blocks
    if len(parts) != 8:
        return False

    for block in parts:
        if len(block) != 6 or not block.isdigit():
            return False

        # dislocker rule seen in your error: mod-11 constraint
        if int(block) % 11 != 0:
            return False

    return True


# ---------------------------
# Check image type
# ---------------------------
def check_image():
    print("[*] Checking image...")

    try:
        result = run(["dislocker-metadata", "-V", IMAGE])

        if result.returncode != 0:
            print("[!] Metadata tool failed")
            print(result.stderr.strip())
            return False

        if "bitlocker" not in result.stdout.lower():
            print("[!] Not BitLocker or metadata hidden")
            return False

        print("[+] BitLocker volume confirmed")
        return True

    except FileNotFoundError:
        print("[!] dislocker-metadata not installed")
        return False


# ---------------------------
# Try unlock
# ---------------------------
def try_key(key: str) -> bool:
    if os.path.exists(DISLOCKER_OUT):
        os.remove(DISLOCKER_OUT)

    cmd = [
        "dislocker",
        "-V", IMAGE,
        f"-p{key}",   # IMPORTANT: no space, no equals sign
        "--", MOUNT_DIR
    ]

    try:
        result = run(cmd, timeout=10)

        if os.path.exists(DISLOCKER_OUT) and os.path.getsize(DISLOCKER_OUT) > 0:
            print("    [+] Decryption output detected")
            return True

    except subprocess.TimeoutExpired:
        print("    [-] Timeout")

    return False


# ---------------------------
# Main loop
# ---------------------------
def main():
    if not os.path.exists(IMAGE):
        print("[-] Image not found")
        return

    if not check_image():
        print("[-] Aborting")
        return

    print("[*] Processing wordlist...\n")

    with open(WORDLIST, "r", errors="ignore") as f:
        for i, line in enumerate(f, 1):

            raw = line.strip()
            key = normalize_key(raw)

            # Step 1: structural validation
            if not re.match(r"^(\d{6}-){7}\d{6}$", key):
                print(f"[{i}] Skip (bad format): {raw}")
                continue

            # Step 2: BitLocker checksum validation
            if not is_valid_bitlocker_key(key):
                #print(f"[{i}] Skip (checksum fail): {key}")
                continue

            print(f"[{i}] Trying: {key}")

            if try_key(key):
                print("\n[+] SUCCESS")
                print(f"[+] Key: {key}")
                print(f"[+] Output: {MOUNT_DIR}")

                print("\n[*] Next step:")
                print(f"    sudo mount -o loop {DISLOCKER_OUT} /mnt/inner")
                return

    print("\n[-] No valid key found")


if __name__ == "__main__":
    main()