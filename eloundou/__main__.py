"""Allow running as: python -m eloundou

Dispatches to runner or compare subcommands.
"""
import sys


def main():
    print("Eloundou replication package")
    print()
    print("Subcommands:")
    print("  python -m eloundou.runner   Run the replication (see --help)")
    print("  python -m eloundou.compare  Compare results to Eloundou labels (see --help)")
    print()
    print("Quick start:")
    print("  python -m eloundou.runner --model gpt-4-0613 --soc-set pilot --seed 137")
    print("  python -m eloundou.compare eloundou/results/gpt-4-0613-full-923/")
    sys.exit(0)


if __name__ == "__main__":
    main()
