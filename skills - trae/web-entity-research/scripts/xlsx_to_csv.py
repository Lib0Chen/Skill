import sys

import pandas as pd


def main():
    if len(sys.argv) < 3:
        raise SystemExit("Usage: py xlsx_to_csv.py <input.xlsx> <output.csv>")

    xlsx_path = sys.argv[1]
    csv_path = sys.argv[2]
    df = pd.read_excel(xlsx_path, keep_default_na=False)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()

