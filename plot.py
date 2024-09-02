import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def rename_column(name: str) -> str:
    if name.startswith("took_"):
        name = name[5:]
    if name == "rust":
        name = "python & rust"
    return name


def main(fn: str, out_dir: str) -> None:
    results = pd.read_csv(fn)
    results.rename(columns=rename_column, inplace=True)

    results_by_direction = {
        "Deserialization": results[results["name"].str.endswith("_de")],
        "Serialization": results[results["name"].str.endswith("_se")],
    }

    for direction, df in results_by_direction.items():
        df.loc[:, "name"] = df["name"].str[:-3]
        df = df.assign(speedup=df["python"] / df["python & rust"])

        fig, ax2 = plt.subplots()
        df.plot(
            x="name",
            y=["python", "python & rust"],
            ax=ax2,
            kind="bar",
            title=direction,
            xlabel="workload",
            ylabel="time [s]",
            logy=True,
            rot=45,
        )
        # ax2.grid(axis="y")
        ax2.grid(axis="y", which="major", alpha=0.5)
        ax2.grid(axis="y", which="minor", alpha=0.2, linestyle="--")
        # ax2.set_ylim(bottom=0.1)
        plt.xticks(rotation=45)
        ax2.tick_params(axis="x", length=0, pad=10)
        plt.table(
            cellText=[df["speedup"].round(2).values],
            rowLabels=["speedup"],
            colLabels=None,
            loc="bottom",
            cellLoc="center",
            rowLoc="center",
        )
        plt.savefig(
            Path(out_dir) / f"{direction.lower()}.png", bbox_inches="tight"
        )
    print(results)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input-csv> <output-dir>")
        sys.exit(1)
    main(*sys.argv[1:3])
