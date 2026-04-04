# See README for details

import sys
import time

combinator+.__doc__ = "Combinators 2-3 wordlists. \nUsage: combinator+.py <wordlist1> \\
<wordlist2> <wordlist3, optional> <output>"

# Gets the number of lines in the wordlist and the average length
# of those lines. Used to ballpark how long the resulting wordlist
# will be.
def analyze_file(filepath):
    total_len = 0
    count = 0

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            # Adds the length of the line to the running sum
            total_len += len(line)
            # Adds 1 line to the line counter
            count += 1

    # Gets the average line length
    avg_len = total_len / count if count else 0

    # Returns a tuple containing the number of lines (count)
    # in the file and the average length of those lines
    return count, avg_len

def human_readable_size(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def confirm_estimate(files):
    stats = [analyze_file(f) for f in files]

    # Gets the number of lines in all files
    counts = [s[0] for s in stats]

    # Gets the average line length of all files
    avgs = [s[1] for s in stats]

    total_lines = 1
    for c in counts:
        total_lines *= c

    avg_line_length = sum(avgs) + 1

    estimated_size = total_lines * avg_line_length

    print("\n=== Estimate ===")
    print(f"Total output lines: {total_lines:,}")
    print(f"Estimated output file size: {human_readable_size(estimated_size)}")

    response = input("Continue? (y/n): ").strip().lower()
    return response == "y", total_lines

# This just prints the progress bar. Contains the number of lines to write, 
# how many have been written, and an ETA
def progress_printer(start_time, written, total):
    elapsed = time.time() - start_time
    if elapsed == 0:
        return

    speed = written / elapsed
    percent = (written / total) * 100 if total else 0
    remaining = (total - written) / speed if speed > 0 else 0

    print(
        f"\r{written:,}/{total:,} ({percent:.2f}%) | "
        f"{speed:,.0f} lines/sec | ETA: {int(remaining)}s",
        end="",
        flush=True
    )

# This actually combinates the files
def stream_combine(files, outfile, total_lines):
    start_time = time.time()
    last_update = start_time
    written = 0

    update_interval = 2  # seconds

    # This runs if there are 2 input files
    if len(files) == 2:
        f1, f2 = files

        with open(f1, "r", encoding="utf-8", errors="ignore") as file1, \
             open(f2, "r", encoding="utf-8", errors="ignore") as file2, \
             open(outfile, "w", encoding="utf-8") as out:

            list2 = [l.strip() for l in file2 if l.strip()]

            for line1 in file1:
                line1 = line1.strip()
                if not line1:
                    continue

                for line2 in list2:
                    out.write(line1 + line2 + "\n")
                    written += 1

                    now = time.time()
                    if now - last_update >= update_interval:
                        progress_printer(start_time, written, total_lines)
                        last_update = now

    # This runs if there are 3 input files
    else:
        f1, f2, f3 = files

        with open(f1, "r", encoding="utf-8", errors="ignore") as file1, \
             open(f2, "r", encoding="utf-8", errors="ignore") as file2, \
             open(f3, "r", encoding="utf-8", errors="ignore") as file3, \
             open(outfile, "w", encoding="utf-8") as out:

            list2 = [l.strip() for l in file2 if l.strip()]
            list3 = [l.strip() for l in file3 if l.strip()]

            # Because this is reading from disk, strips any witespace
            for line1 in file1:
                line1 = line1.strip()
                if not line1:
                    continue

                # This creates the combinator string and writes to output
                for line2 in list2:
                    for line3 in list3:
                        out.write(line1 + line2 + line3 + "\n")
                        written += 1

                        now = time.time()
                        if now - last_update >= update_interval:
                            progress_printer(start_time, written, total_lines)
                            last_update = now

    # final update
    progress_printer(start_time, written, total_lines)
    print("\nDone.")


def main():
    if len(sys.argv) not in [4, 5]:
        print("Usage:")
        print("  python combinator+.py wordlist1 wordlist2 outputwordlist")
        print("  python combinator+.py wordlist1 wordlist2 wordlist3 outputwordlist")
        sys.exit(1)

    *input_files, output_file = sys.argv[1:]

    proceed, total_lines = confirm_estimate(input_files)

    if not proceed:
        print("Aborted.")
        sys.exit(0)

    print("Generating...\n")
    stream_combine(input_files, output_file, total_lines)


if __name__ == "__main__":
    main()