import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def load_config():
    cfg_path = Path(__file__).resolve().parents[1] / "config.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def parse_date(s: str) -> datetime | None:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def build_history(raw_text: str, date_rx: re.Pattern, value_rx: re.Pattern, align_strategy: str):
    dates = date_rx.findall(raw_text or "")
    values = value_rx.findall(raw_text or "")

    dates = [d[0] if isinstance(d, tuple) else d for d in dates]
    values = [v[0] if isinstance(v, tuple) else v for v in values]

    if align_strategy == "reverse_zip":
        dates = list(reversed(dates))
        values = list(reversed(values))

    history = []
    for i in range(min(len(dates), len(values))):
        dt = parse_date(dates[i])
        if dt is None:
            continue
        history.append({"date": dt, "Target_Value": str(values[i]).strip()})

    return history, len(dates), len(values)


def pick_latest_at_or_before(history, cutoff_dt: datetime):
    valid = [h for h in history if h["date"] <= cutoff_dt]
    if not valid:
        return "Manual Check", "N/A"
    latest = max(valid, key=lambda x: x["date"])
    return latest["Target_Value"], latest["date"].strftime("%d-%b-%Y")


def main():
    cfg = load_config()
    out_cfg = cfg.get("output") or {}
    scraped_csv = out_cfg.get("scraped_data_csv") or "scraped_data.csv"
    out_csv = out_cfg.get("final_csv") or "final_report.csv"
    out_xlsx = out_cfg.get("final_xlsx") or "final_report.xlsx"

    parser_cfg = cfg.get("parser") or {}
    date_regex = parser_cfg.get("date_regex") or r"(\d{2}-[A-Za-z]{3}-\d{4})"
    value_regex = parser_cfg.get("target_value_regex") or r"([A-Za-z0-9+()\-]{1,20})"
    align_strategy = parser_cfg.get("align_strategy") or "zip"
    cutoffs = parser_cfg.get("cutoffs") or []

    date_rx = re.compile(date_regex)
    value_rx = re.compile(value_regex)

    df = pd.read_csv(scraped_csv)
    for col in ("Search_Key", "Target_URL", "raw_content"):
        if col not in df.columns:
            raise ValueError(f"{scraped_csv} 缺少列: {col}")

    rows = []
    mismatch_rows = []

    for _, r in df.iterrows():
        search_key = str(r.get("Search_Key", "")).strip()
        target_url = str(r.get("Target_URL", "")).strip()
        raw_text = str(r.get("raw_content", "") or "")

        history, date_count, value_count = build_history(raw_text, date_rx, value_rx, align_strategy)
        if date_count != value_count and (date_count > 0 or value_count > 0):
            mismatch_rows.append({"Search_Key": search_key, "Target_URL": target_url, "dates": date_count, "values": value_count})

        out_row = {"Search_Key": search_key, "Target_URL": target_url}

        if cutoffs:
            for c in cutoffs:
                label = str(c.get("label", "")).strip() or str(c.get("cutoff", "")).strip()
                cutoff_dt = parse_date(str(c.get("cutoff", "")).strip())
                if cutoff_dt is None:
                    continue
                v, d = pick_latest_at_or_before(history, cutoff_dt)
                out_row[f"Target_Value_{label}"] = v
                out_row[f"Target_Date_{label}"] = d
        else:
            out_row["Target_Value"] = "Manual Check" if not history else history[0]["Target_Value"]
            out_row["Target_Date"] = "N/A" if not history else history[0]["date"].strftime("%d-%b-%Y")

        rows.append(out_row)

    out_df = pd.DataFrame(rows)
    out_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    try:
        out_df.to_excel(out_xlsx, index=False)
    except PermissionError:
        pass

    if mismatch_rows:
        mismatch_df = pd.DataFrame(mismatch_rows)
        mismatch_df.to_csv("parser_mismatch.csv", index=False, encoding="utf-8-sig")
        for m in mismatch_rows:
            print(f"[数量不匹配] {m['Search_Key']} dates={m['dates']} values={m['values']}")


if __name__ == "__main__":
    main()
