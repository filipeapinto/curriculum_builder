A correct version of parse_csv.py satisfies all of the following:

1. `revenue_by_customer(path)` returns a dict mapping each customer name found in the
   CSV to the sum of that customer's `amount` values.
2. It works when a customer appears for the first time, and when the same customer
   appears on multiple rows.
3. It works on a CSV with a header row `customer,amount` and one or more data rows.
4. It does not raise on any well-formed input matching that shape.
