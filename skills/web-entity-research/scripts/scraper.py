import json
import re
import time
from pathlib import Path

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def load_config():
    cfg_path = Path(__file__).resolve().parents[1] / "config.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def safe_filename(s: str, max_len: int = 120) -> str:
    s = normalize_spaces(s)
    s = re.sub(r"[<>:\"/\\\\|?*\x00-\x1F]", "_", s)
    s = s.strip(" ._")
    if not s:
        s = "item"
    return s[:max_len]


def accept_cookies_if_present(page, selectors):
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=3000)
                return
        except Exception:
            continue


def main():
    cfg = load_config()
    cookie_selectors = cfg.get("cookie_accept_selector") or []
    content_root = cfg.get("content_root_selector")

    out_cfg = cfg.get("output") or {}
    verified_csv = out_cfg.get("verified_mapping_csv") or "verified_mapping.csv"
    out_csv = out_cfg.get("scraped_data_csv") or "scraped_data.csv"
    screenshots_dir = Path(out_cfg.get("screenshots_dir") or "screenshots").resolve()
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    browser_cfg = cfg.get("browser") or {}
    channel = browser_cfg.get("channel", "chrome")
    headless = bool(browser_cfg.get("headless", False))
    slow_mo = int(browser_cfg.get("slow_mo_ms", 0))
    timeout_ms = int(browser_cfg.get("timeout_ms", 60000))

    df = pd.read_csv(verified_csv)
    for col in ("Search_Key", "Target_URL"):
        if col not in df.columns:
            raise ValueError(f"{verified_csv} 缺少列: {col}")

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=channel, headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        for i, row in df.iterrows():
            search_key = str(row.get("Search_Key", "")).strip()
            target_url = str(row.get("Target_URL", "")).strip()
            if not search_key or not target_url or target_url == "Not Found":
                results.append(
                    {
                        "Search_Key": search_key,
                        "Target_URL": target_url,
                        "raw_content": "",
                        "screenshot_path": "",
                        "note": "no_url",
                    }
                )
                continue

            screenshot_path = str((screenshots_dir / f"{i+1:03d}_{safe_filename(search_key)}.png").resolve())
            raw_content = ""
            note = ""

            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=timeout_ms)
                accept_cookies_if_present(page, cookie_selectors)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PlaywrightTimeoutError:
                    pass

                if content_root:
                    loc = page.locator(content_root).first
                    try:
                        loc.wait_for(timeout=15000)
                        raw_content = loc.inner_text(timeout=5000)
                    except Exception:
                        raw_content = page.locator("body").inner_text(timeout=5000)
                        note = "content_root_not_found"
                else:
                    raw_content = page.locator("body").inner_text(timeout=5000)

                try:
                    page.screenshot(path=screenshot_path, full_page=True)
                except Exception:
                    screenshot_path = ""
            except Exception:
                note = "goto_failed"
                try:
                    page.screenshot(path=screenshot_path, full_page=True)
                except Exception:
                    screenshot_path = ""

            results.append(
                {
                    "Search_Key": search_key,
                    "Target_URL": target_url,
                    "raw_content": raw_content,
                    "screenshot_path": screenshot_path,
                    "note": note,
                }
            )
            time.sleep(1)

        out = pd.DataFrame(results)
        out.to_csv(out_csv, index=False, encoding="utf-8-sig")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
