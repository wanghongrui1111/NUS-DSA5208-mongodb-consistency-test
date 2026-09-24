"""The deliberately small concern and routing matrix used by every v5 scenario."""

from itertools import product

READ_CONCERNS = ("local", "majority")
WRITE_CONCERNS = (1, "majority")
PREFERENCES = ("primary", "primaryPreferred", "secondaryPreferred")
CAUSAL = (False, True)


def _make_cells():
    rows = []
    for index, (rc, wc, preference, causal) in enumerate(
            product(READ_CONCERNS, WRITE_CONCERNS, PREFERENCES, CAUSAL), start=1):
        rows.append({
            "id": f"rc={rc}|wc={wc}|pref={preference}|causal={'on' if causal else 'off'}",
            "rc": rc, "wc": wc, "preference": preference, "causal": causal,
            "v1": index * 2 - 1, "v2": index * 2,
        })
    return tuple(rows)


CELLS = _make_cells()


def cells(only=None):
    """Return requested cells in a stable order; ``only`` is a comma key=value filter."""
    filters = {} if only is None else dict(part.split("=", 1) for part in only.split(","))

    def view(row):
        return {**row, "causal": "on" if row["causal"] else "off"}

    return [row for row in CELLS if all(view(row).get(key) == value for key, value in filters.items())]
