# See README for details

import re
import argparse
import csv
from collections import Counter, defaultdict

correlog.py.__doc__="Extracting information from a log using REGEX. \nUsage: correlog.py <log file> '<regex>'"

# TODO: Document :)

def normalize(value):
    if value is None:
        return None
    return value.strip()


def get_ranked_items(counter, top_n, bottom=False):
    items = counter.most_common()
    if bottom:
        return items[-top_n:] if top_n <= len(items) else items
    return items[:top_n]


def sort_by_value_length(mapping, top_n, bottom=False):
    items = [(k, len(set(v))) for k, v in mapping.items()]
    items_sorted = sorted(items, key=lambda x: x[1], reverse=True)

    if bottom:
        return items_sorted[-top_n:] if top_n <= len(items_sorted) else items_sorted
    return items_sorted[:top_n]


def analyze_log(file_path, pattern, group_indices=(0,), verbose=False, top_n=10, csv_path=None, bottom=False):
    regex = re.compile(pattern)

    counter = Counter()
    total_matches = 0

    all_values_numeric = True
    values_as_int_single = []

    pair_counter = Counter()
    group1_to_group2 = defaultdict(list)

    numeric_values_per_group = [[], []]

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            for match in regex.finditer(line):
                try:
                    raw_values = tuple(match.group(i) for i in group_indices)
                except IndexError:
                    print(f"Invalid group index in: {group_indices}")
                    return

                values = tuple(normalize(v) for v in raw_values)

                if any(v is None for v in values):
                    continue

                # =========================
                # Single-group mode
                # =========================
                if len(group_indices) == 1:
                    value = values[0]

                    counter[value] += 1
                    total_matches += 1

                    try:
                        num = int(value)
                        values_as_int_single.append(num)
                    except ValueError:
                        all_values_numeric = False

                # =========================
                # Dual-group mode
                # =========================
                elif len(group_indices) == 2:
                    g1, g2 = values

                    pair_counter[(g1, g2)] += 1
                    group1_to_group2[g1].append(g2)

                    total_matches += 1

                    try:
                        numeric_values_per_group[0].append(int(g1))
                    except ValueError:
                        pass

                    try:
                        numeric_values_per_group[1].append(int(g2))
                    except ValueError:
                        pass

    print("\n--- Analysis Results ---")

    # =========================
    # Single-group output
    # =========================
    if len(group_indices) == 1:
        print(f"Total matches: {total_matches}")
        print(f"Unique matches: {len(counter)}\n")

        if all_values_numeric and values_as_int_single:
            avg = sum(values_as_int_single) / len(values_as_int_single)
            print(f"Average of matches: {avg:.2f}")
        else:
            print("Average of matches: N/A (non-numeric values present)\n")

        items = get_ranked_items(counter, top_n, bottom)

        label = "Bottom" if bottom else "Top"
        print(f"{label} {top_n} occurrences:")

        for value, count in items:
            print(f"{value}: {count}")

        if csv_path:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["value", "count"])
                for value, count in counter.most_common():
                    writer.writerow([value, count])

            print(f"\nCSV exported to: {csv_path}")

    # =========================
    # Dual-group output
    # =========================
    elif len(group_indices) == 2:
        print(f"Total matched pairs: {total_matches}")
        print(f"Unique pairs: {len(pair_counter)}\n")

        # Averages per group
        print("Average per group:")
        for idx in range(2):
            values = numeric_values_per_group[idx]
            if values:
                avg = sum(values) / len(values)
                print(f"Group {group_indices[idx]} average: {avg:.2f}")
            else:
                print(f"Group {group_indices[idx]} average: N/A")

        print()

        # --- Pairs ---
        pair_items = pair_counter.most_common()
        if bottom:
            pair_items = pair_items[-top_n:] if top_n <= len(pair_items) else pair_items
            label = "Bottom"
        else:
            pair_items = pair_items[:top_n]
            label = "Top"

        print(f"{label} {top_n} matched pairs:")
        for pair, count in pair_items:
            print(f"{pair[0]}:{pair[1]} -> {count}")

        # --- Unique associations ---
        print("\nGroup 1 → Group 2 associations (unique counts):")

        grouped_items = [(g1, len(set(g2_list))) for g1, g2_list in group1_to_group2.items()]

        # Sort descending by default
        grouped_items.sort(key=lambda x: x[1], reverse=not bottom)

        if bottom:
            selected_items = grouped_items[:top_n]
            label = "Bottom"
        else:
            selected_items = grouped_items[:top_n]
            label = "Top"

        print(f"{label} {top_n} by unique associated values:")

        for g1, count in selected_items:
            print(f"{g1}: {count} unique values")

        # --- Averages per Group1 ---
        print("\nGroup 1 → average of associated Group 2 values:")

        group_averages = {}

        for g1, g2_list in group1_to_group2.items():
            numeric_vals = []

            for v in g2_list:
                try:
                    numeric_vals.append(int(v))
                except ValueError:
                    pass

            if numeric_vals:
                group_averages[g1] = sum(numeric_vals) / len(numeric_vals)

        avg_items = sorted(group_averages.items(), key=lambda x: x[1])

        if not bottom:
            avg_items = avg_items[::-1]

        if bottom:
            avg_items = avg_items[:top_n]
            label = "Bottom"
        else:
            avg_items = avg_items[:top_n]
            label = "Top"

        print(f"{label} {top_n} averages:")

        for g1, avg in avg_items:
            print(f"{g1}: average = {avg:.2f}")

        if csv_path:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow(["section", "key", "value", "extra"])

                for (g1, g2), count in pair_counter.most_common():
                    writer.writerow(["pair", f"{g1}:{g2}", count, "count"])

                for g1, g2_list in group1_to_group2.items():
                    writer.writerow(["group1_unique", g1, len(set(g2_list)), "unique_count"])

                for g1, avg in group_averages.items():
                    writer.writerow(["group1_average", g1, avg if avg is not None else "", "average"])

            print(f"\nCSV exported to: {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze log files using regex with statistics.")
    parser.add_argument("logfile", help="Path to log file")
    parser.add_argument("regex", help="Regex pattern (use quotes)")

    parser.add_argument(
        "-g", "--group",
        type=int,
        nargs='+',
        default=[0],
        help="One or two regex group indices (e.g. -g 1 or -g 1 2)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print all matches instead of top results"
    )

    parser.add_argument(
        "-n", "--top",
        type=int,
        default=10,
        help="Number of results to show (default: 10)"
    )

    parser.add_argument(
        "-b", "--bottom",
        action="store_true",
        help="Show the bottom N results instead of top N"
    )

    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Output results to CSV file"
    )

    args = parser.parse_args()

    if len(args.group) not in (1, 2):
        print("Error: --group must have either 1 or 2 integers.")
        return

    analyze_log(
        args.logfile,
        args.regex,
        group_indices=tuple(args.group),
        verbose=args.verbose,
        top_n=args.top,
        csv_path=args.csv,
        bottom=args.bottom
    )


if __name__ == "__main__":
    main()