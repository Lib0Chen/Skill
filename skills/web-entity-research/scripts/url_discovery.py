import json
import time
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def load_config():
    cfg_path = Path(__file__).resolve().parents[1] / "config.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))


def accept_cookies_if_present(page, selectors):
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                loc.first.click(timeout=3000)
                return
        except Exception:
            continue


def first_href(page, selectors):
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                href = loc.get_attribute("href")
                if href:
                    return href
        except Exception:
            continue
    return None


def main():
    cfg = load_config()
    base_url = cfg["base_url"]
    search_tpl = cfg["search_url_template"]
    cookie_selectors = cfg.get("cookie_accept_selector") or []
    result_selectors = cfg.get("result_selector") or ["a[href]"]

    mapping_csv = "mapping.csv"
    out_csv = (cfg.get("output") or {}).get("verified_mapping_csv") or "verified_mapping.csv"

    browser_cfg = cfg.get("browser") or {}
    channel = browser_cfg.get("channel", "chrome")
    headless = bool(browser_cfg.get("headless", False))
    slow_mo = int(browser_cfg.get("slow_mo_ms", 0))
    timeout_ms = int(browser_cfg.get("timeout_ms", 60000))

    df = pd.read_csv(mapping_csv)
    if "Search_Key" not in df.columns or "Search_Query" not in df.columns:
        raise ValueError("mapping.csv 必须包含列：Search_Key, Search_Query")

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel=channel, headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(timeout_ms)

        page.goto(base_url, wait_until="domcontentloaded")
        accept_cookies_if_present(page, cookie_selectors)
        time.sleep(2)

        for _, r in df.iterrows():
            search_key = str(r.get("Search_Key", "")).strip()
            search_query = str(r.get("Search_Query", "")).strip()
            if not search_key or not search_query:
                continue

            target_url = "Not Found"
            note = ""
            query = quote_plus(search_query)
            search_url = search_tpl.format(query=query)

            try:
                page.goto(search_url, wait_until="domcontentloaded", timeout=timeout_ms)
                accept_cookies_if_present(page, cookie_selectors)
                try:
                    page.wait_for_selector(",".join(result_selectors), timeout=15000)
                except PlaywrightTimeoutError:
                    pass

                href = first_href(page, result_selectors)
                if href:
                    target_url = href if href.startswith("http") else f"{base_url}{href}"
                else:
                    target_url = "Not Found"
                    note = "no_result_link"
            except Exception:
                target_url = "Not Found"
                note = "goto_failed"

            results.append({"Search_Key": search_key, "Search_Query": search_query, "Target_URL": target_url, "Note": note})
            time.sleep(1)

        out = pd.DataFrame(results)
        out.to_csv(out_csv, index=False, encoding="utf-8-sig")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
