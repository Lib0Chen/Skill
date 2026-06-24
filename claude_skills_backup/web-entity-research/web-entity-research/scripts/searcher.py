def main() -> None:
    import runpy
    from pathlib import Path

    runpy.run_path(str((Path(__file__).resolve().parent / "url_discovery.py").resolve()), run_name="__main__")


if __name__ == "__main__":
    main()
