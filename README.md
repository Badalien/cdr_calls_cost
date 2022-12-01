## Description

This simple code allow to calculate billed calls cost in a large CDR files

> CDR - Call Detail Record. It includes such details as the duration and time of call, what number the call was initiated from and the destination number, and so on.

You just need no define path to CDR file and prices file in variables: `cdr_file` and `prices_file` in **set_costs.py**

> Prices file should contain fields: `Code`, `Price`, and biling parametrs: 
> - `MC` - the minimal number of seconds to be paid
> - `CI` – charging interval (1 – rating per second)

> Columns of CDR file should be defined in data structure CallRow(TypedDict), where keys is a columns header
