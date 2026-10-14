import json
import itertools
import os

def load_substitutions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_wordlist(base_word, subs):
    options = []

    for char in base_word:
        char_options = set()

        # Add mixed case variants
        if char.isalpha():
            char_options.add(char.lower())
            char_options.add(char.upper())

        # Add substitutions (case-insensitive lookup)
        key = char.upper()
        if key in subs:
            for sub in subs[key]:
                char_options.add(sub)

        # Always ensure at least original char is included
        char_options.add(char)

        options.append(list(char_options))

    for combo in itertools.product(*options):
        yield "".join(combo)

def main():
    json_file = "/home/ctf/substitutions.json"
    base_word = input("Enter base word: ").strip()
    output_file = "/home/ctf/l33tsp3ak-wordlist.txt"

    substitutions = load_substitutions(json_file)

    # Load existing words if file exists (to avoid duplicates)
    existing = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                existing.add(line.strip())

    print("\nGenerating wordlist...\n")

    new_count = 0
    total_written = 0

    # Append mode instead of overwrite
    with open(output_file, "a", encoding="utf-8") as out:
        for word in generate_wordlist(base_word, substitutions):
            if word not in existing:
                out.write(word + "\n")
                existing.add(word)
                new_count += 1
            total_written += 1

    print(f"Done.")
    print(f"New words added: {new_count}")
    print(f"Total processed: {total_written}")

if __name__ == "__main__":
    main()