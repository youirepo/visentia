"""Allow `python -m visentia <prompt>` as an alternative entry point to the console script."""

from visentia.app_shell import main

if __name__ == "__main__":
    main()
