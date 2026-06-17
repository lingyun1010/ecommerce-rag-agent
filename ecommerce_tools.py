from pathlib import Path


PRODUCTS_PATH = Path("data/products.md")


def _is_markdown_table_separator(line):
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)


def _parse_markdown_table_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def load_product_rows(path=PRODUCTS_PATH):
    rows = []
    headers = None

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        if _is_markdown_table_separator(line):
            continue

        cells = _parse_markdown_table_row(line)
        if headers is None:
            headers = cells
            continue

        if len(cells) != len(headers):
            continue

        rows.append(dict(zip(headers, cells)))

    return rows


def is_product_count_question(question):
    normalized = question.lower()
    product_terms = ("product", "products", "item", "items")
    count_terms = (
        "how many",
        "number of",
        "count",
        "total",
        "catalogue size",
        "catalog size",
    )

    return any(term in normalized for term in product_terms) and any(
        term in normalized for term in count_terms
    )


def answer_structured_question(question, product_rows):
    if is_product_count_question(question):
        count = len(product_rows)
        return (
            f"MURA currently has {count} product records in the local product "
            "catalogue. This count comes directly from data/products.md rather "
            "than vector similarity retrieval."
        )

    return None
