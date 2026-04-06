"Attacks WPA PMKs. Usage: wpa_pmk_cracker.py <wpa_supplicant> <wordlist>"

#NOTICE: This is a stupid way of doing this. See README for details

import hashlib
import binascii
import sys
import json
import argparse
import re
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

# For anyone curious, this is generated using the Linux wpa_supplicant application
TEST_SSID = "homeWifi"
TEST_PASSWORD = "thisisatestpassword1"
TEST_EXPECTED_PSK = "f65e61758b86994a9504928405289efe34eadf581ceff6bfe55b3ecba989f589"

# Ingests the wpa_supplicant information from the targets file.
# Is so long because it's built to accept regular JSON as well
# as wpa_supplicant's naitive format
def load_targets(path):
    try:
        with open(path, "r") as f:
            content = f.read()

        targets = []

        # --- Try JSON first ---
        try:
            data = json.loads(content)

            # Handle list of objects
            if isinstance(data, list):
                for entry in data:
                    ssid = entry.get("ssid")
                    pmk = entry.get("pmk") or entry.get("psk")

                    if ssid and pmk:
                        targets.append((ssid, pmk))

            # Handle single object
            elif isinstance(data, dict):
                ssid = data.get("ssid")
                pmk = data.get("pmk") or data.get("psk")

                if ssid and pmk:
                    targets.append((ssid, pmk))

        except json.JSONDecodeError:
            pass  # fall through to supplicant parser

        # --- Fallback: parse wpa_supplicant-style blocks ---
        if not targets:
            blocks = re.findall(r'network=\{([^}]*)\}', content, re.DOTALL)

            for block in blocks:
                ssid_match = re.search(r'ssid="?([^"\n]+)"?', block)
                psk_match = re.search(r'psk="?([0-9a-fA-F]{64})"?', block)

                if ssid_match and psk_match:
                    ssid = ssid_match.group(1).strip()
                    pmk = psk_match.group(1).strip()
                    targets.append((ssid, pmk))

        # --- Validation ---
        if not targets:
            raise ValueError("No valid targets found in file")

        # --- Output ---
        print(f"[+] Loaded {len(targets)} targets from {path}\n")

        for i, (ssid, pmk) in enumerate(targets, 1):
            print(f"  [{i}] SSID: {ssid}")
            print(f"      PMK : {pmk}")

        print()
        return targets

    except Exception as e:
        print(f"Error loading targets file: {e}")
        sys.exit(1)

# This preforms the math to calculate the guess PMK
# based on the network's SSID and the guess password
def derive_psk(password, ssid_local):
    dk = hashlib.pbkdf2_hmac(
        'sha1',
        password.encode('utf-8'),
        ssid_local.encode('utf-8'),
        4096,
        32
    )
    return binascii.hexlify(dk).decode()

# This attacks the known TEST PMK with the known correct
# password to make sure everything is working
def worker_self_test():
    return derive_psk(TEST_PASSWORD, TEST_SSID) == TEST_EXPECTED_PSK

# This preforms the actual guess
def check_password(password, targets):
    password = password.strip()
    if not password:
        return None

    for ssid, target_psk in targets:
        if derive_psk(password, ssid) == target_psk:
            return (ssid, password)

    return None

# This is what is preformed by the workers. Mostly just guessing passwords
def process_batch(batch, executor, total_checked, targets):
    futures = [
        executor.submit(check_password, pw, targets)
        for pw in batch
    ]

    completed = 0
    found_targets = []

    for future in as_completed(futures):
        completed += 1
        result = future.result()

        current_total = total_checked + completed

        if current_total % 1000 == 0:
            print(
                f"Checked: {current_total} | Remaining targets: {len(targets)}",
                end="\r",
                flush=True
            )

        if result:
            ssid, password = result
            print()
            print(f"[+] Match found! SSID: {ssid} | Password: {password}")
            found_targets.append((ssid, password))

    return found_targets

# This is the main function. This function calls the workers to guess passwords
def crack_wordlist_streaming(wordlist_path, targets, workers=6, batch_size=5000):
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:

            print("[*] Running worker self-test...")
            if not executor.submit(worker_self_test).result():
                print("[-] Worker self-test FAILED. Aborting.")
                return
            print("[+] Worker self-test PASSED\n")

            print(f"[*] Starting with {len(targets)} targets\n")

            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                batch = []
                total_checked = 0

                for line in f:
                    if not targets:
                        print("\n[+] All targets cracked!")
                        return

                    pw = line.strip()
                    if not pw:
                        continue

                    batch.append(pw)

                    if len(batch) >= batch_size:
                        found = process_batch(batch, executor, total_checked, targets)

                        # Remove cracked targets
                        for ssid, _ in found:
                            targets = [t for t in targets if t[0] != ssid]

                        total_checked += len(batch)
                        batch = []

                # Process remaining batch
                if batch and targets:
                    found = process_batch(batch, executor, total_checked, targets)

                    for ssid, _ in found:
                        targets = [t for t in targets if t[0] != ssid]

        print()
        if targets:
            print(f"[-] Done. Remaining targets not cracked: {len(targets)}")
        else:
            print("[+] All targets cracked!")

    except FileNotFoundError:
        print(f"Error: File not found -> {wordlist_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WPA2 PMK Cracker (educational)")

    parser.add_argument("targets", help="Path to JSON targets file")
    parser.add_argument("wordlist", help="Path to wordlist file")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Number of worker processes")
    parser.add_argument("-b", "--batch", type=int, default=1000, help="Batch size")

    args = parser.parse_args()

    targets = load_targets(args.targets)

    crack_wordlist_streaming(
        args.wordlist,
        targets,
        workers=args.workers,
        batch_size=args.batch
    )