"""Parse a CSV of orders and return total revenue per customer."""
import csv


def revenue_by_customer(path):
    totals = {}
    with open(path) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            cust = row["customer"]
            totals[cust] = totals.get(cust, 0.0) + float(row["amount"])
    return totals
