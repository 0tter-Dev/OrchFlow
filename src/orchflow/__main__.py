"""Command-line module entrypoint for ``python -m orchflow``."""


def main() -> None:
    """Run the default OrchFlow CLI entrypoint."""
    from orchflow.external.cli.app import run

    run()


if __name__ == "__main__":
    main()
