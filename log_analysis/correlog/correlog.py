"Extracting information from a log using REGEX. \nUsage: correlog.py <log file> '<regex>' <arguments, optional>"

import re
import argparse
import csv
from collections import Counter, defaultdict, deque


def normalize(value):
    if value is None:
        return None
    return value.strip()


def try_parse_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def apply_limit(items, top_n, bottom, verbose):
    if verbose:
        return items[::-1] if bottom else items

    if bottom:
        return items[-top_n:] if top_n <= len(items) else items
    return items[:top_n]


def get_counter_items(counter, top_n, bottom, verbose):
    items = counter.most_common()
    return apply_limit(items, top_n, bottom, verbose)


def compute_average(values):
    return (sum(values) / len(values)) if values else None


def process_match(values,
                  counter, numeric_values_single,
                  pair_counter, group1_to_group2,
                  numeric_values_per_group):
    if len(values) == 1:
        value = values[0]
        counter[value] += 1

        num = try_parse_number(value)
        if num is not None:
            numeric_values_single.append(num)

    elif len(values) == 2:
        g1, g2 = values

        pair_counter[(g1, g2)] += 1
        group1_to_group2[g1].append(g2)

        num1 = try_parse_number(g1)
        if num1 is not None:
            numeric_values_per_group[0].append(num1)

        num2 = try_parse_number(g2)
        if num2 is not None:
            numeric_values_per_group[1].append(num2)


def analyze_log(
    file_path,
    pattern,
    group_indices=(0,),
    verbose=False,
    very_verbose=False,
    top_n=10,
    csv_path=None,
    bottom=False,
    multiline=False,
    window_size=0
):
    flags = re.DOTALL if multiline else 0
    regex = re.compile(pattern, flags)

    counter = Counter()
    total_matches = 0

    numeric_values_single = []

    pair_counter = Counter()
    group1_to_group2 = defaultdict(list)
    numeric_values_per_group = [[], []]

    seen_spans = set()

    def process_chunk(chunk, base_offset):
        nonlocal total_matches

        for match in regex.finditer(chunk):
            span = (base_offset + match.start(), base_offset + match.end())

            if span in seen_spans:
                continue
            seen_spans.add(span)

            try:
                if not group_indices:
                    raw_values = (match.group(0),)
                else:
                    raw_values = tuple(match.group(i) for i in group_indices)
            except IndexError:
                print(f"Invalid group index in: {group_indices}")
                return

            values = tuple(normalize(v) for v in raw_values)

            if any(v is None for v in values):
                continue

            # 🔥 VERY VERBOSE OUTPUT
            if very_verbose:
                print(f"[{span[0]}:{span[1]}] -> {' | '.join(values)}")

            process_match(
                values,
                counter,
                numeric_values_single,
                pair_counter,
                group1_to_group2,
                numeric_values_per_group
            )

            total_matches += 1

    # =========================
    # File Processing
    # =========================
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:

        if multiline and window_size > 0:
            window = deque()
            offset = 0

            for line in f:
                window.append(line)

                if len(window) > window_size:
                    removed = window.popleft()
                    offset += len(removed)

                chunk = ''.join(window)
                process_chunk(chunk, offset)

        elif multiline:
            content = f.read()
            process_chunk(content, 0)

        else:
            offset = 0
            for line in f:
                process_chunk(line, offset)
                offset += len(line)

    print("\n--- Analysis Results ---")

    # =========================
    # Single-group output
    # =========================
    if len(group_indices) <= 1:
        print(f"Total matches: {total_matches}")
        print(f"Unique matches: {len(counter)}\n")

        avg = compute_average(numeric_values_single)
        if avg is not None:
            print(f"Average of matches: {avg:.2f}")
        else:
            print("Average of matches: N/A (no numeric values found)\n")

        items = get_counter_items(counter, top_n, bottom, verbose)

        if verbose:
            print("All occurrences:")
        else:
            label = "Bottom" if bottom else "Top"
            print(f"{label} {top_n} occurrences:")

        for value, count in items:
            print(f"{value}: {count}")

    # =========================
    # Dual-group output
    # =========================
    elif len(group_indices) == 2:
        print(f"Total matched pairs: {total_matches}")
        print(f"Unique pairs: {len(pair_counter)}\n")

        print("Average per group:")
        for idx in range(2):
            avg = compute_average(numeric_values_per_group[idx])
            if avg is not None:
                print(f"Group {group_indices[idx]} average: {avg:.2f}")
            else:
                print(f"Group {group_indices[idx]} average: N/A")

        print()

        pair_items = apply_limit(pair_counter.most_common(), top_n, bottom, verbose)

        if verbose:
            print("All matched pairs:")
        else:
            label = "Bottom" if bottom else "Top"
            print(f"{label} {top_n} matched pairs:")

        for (g1, g2), count in pair_items:
            print(f"{g1}:{g2} -> {count}")

        print("\nGroup 1 → Group 2 associations (unique counts):")

        grouped_items = [(g1, len(set(g2_list))) for g1, g2_list in group1_to_group2.items()]
        grouped_items.sort(key=lambda x: x[1], reverse=True)

        grouped_items = apply_limit(grouped_items, top_n, bottom, verbose)

        for g1, count in grouped_items:
            print(f"{g1}: {count} unique values")

    # CSV unchanged for brevity


def main():
    parser = argparse.ArgumentParser(description="Analyze log files using regex with statistics.")
    parser.add_argument("logfile")
    parser.add_argument("regex")

    parser.add_argument("-g", "--group", type=int, nargs='*', default=[0])

    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show all results (no top-N limit)")

    parser.add_argument("-vv", "--very-verbose", action="store_true",
                        help="Print every raw match with position")

    parser.add_argument("-n", "--top", type=int, default=10)
    parser.add_argument("-b", "--bottom", action="store_true")

    parser.add_argument("-m", "--multiline", action="store_true")
    parser.add_argument("-w", "--window", type=int, default=0)

    args = parser.parse_args()

    if len(args.group) > 2:
        print("Error: --group supports at most 2 indices.")
        return

    analyze_log(
        args.logfile,
        args.regex,
        group_indices=tuple(args.group),
        verbose=args.verbose,
        very_verbose=args.very_verbose,
        top_n=args.top,
        bottom=args.bottom,
        multiline=args.multiline,
        window_size=args.window
    )


if __name__ == "__main__":
    main()