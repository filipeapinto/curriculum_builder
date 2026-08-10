split_evenly(total, ways) must:
1. Return a list of `ways` Decimal amounts.
2. Guarantee the parts sum exactly to total, with no lost or invented cents.
3. Distribute any remainder cents one per part, earliest parts first. This must hold
   for negative totals as well as positive ones.
4. Raise ValueError when ways < 1.
