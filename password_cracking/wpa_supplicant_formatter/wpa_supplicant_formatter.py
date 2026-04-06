"Converts WPA Supplicant info to Hashcat format for cracking. Usage: wpa_supplicant_formatter.py <supplicant info> <output file>"

# See README for details

import re
import base64
import sys

def process_networks(input_file, output_file):
    with open(input_file, 'r') as f:
        content = f.read()

    # Extract network blocks
    networks = re.findall(
        r'network=\{\s*ssid="([^"]+)"\s*psk=([a-fA-F0-9]+)\s*\}',
        content
    )

    output_lines = []

    for ssid, psk_hex in networks:
        # SSID -> base64
        ssid_b64 = base64.b64encode(ssid.encode()).decode()

        # PSK hex -> bytes -> base64
        psk_b64 = base64.b64encode(bytes.fromhex(psk_hex)).decode()

        line = f"{ssid}:sha1:4096:{ssid_b64}:{psk_b64}"
        output_lines.append(line)

    with open(output_file, 'w') as f:
        f.write("\n".join(output_lines))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_networks(input_file, output_file)