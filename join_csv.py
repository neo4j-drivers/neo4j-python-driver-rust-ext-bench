import csv
import sys
from collections import defaultdict
from pathlib import Path


csv_paths = sys.argv[1:]
combined_csv_header = ["name"]
combined_csv = defaultdict(list)


for path in map(Path, csv_paths):
    with path.open(newline="") as f:
        combined_csv_header.append(f"took_{path.stem}")
        reader = csv.DictReader(f)
        for row in reader:
            combined_csv[row["name"]].append(row["took"])

writer = csv.writer(sys.stdout)
writer.writerow(combined_csv_header)
for name, timings in combined_csv.items():
    writer.writerow([name] + timings)
sys.stdout.flush()
