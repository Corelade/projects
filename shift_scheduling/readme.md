# Shift Scheduling (Backtracking CSP)

A tiny constraint-solver that builds a weekly rota for multiple departments and three daily shifts using plain Python. It models the problem as a constraint satisfaction problem (CSP) and searches for a valid assignment with backtracking.

# What it does
- Defines departments with max_num_staff (and optional min_num_staff).

- Defines staff with name, role, and contract_hours.

- Generates all domains (e.g. monday_morning_cashier) from days × shifts × departments.

- Uses a backtracking search to assign staff to each domain while enforcing:

    - per-department capacity limits,
    - no double-booking in the same day+shift across departments,
    - no duplicates within a single department shift,
    - a per-person weekly shift limit (default: 14 shifts),
    - global minimums per department for feasibility checks.

- Makes mornings flexible: only the department minimum is required in the morning; afternoon/evening aim for the max.
(This behavior is encapsulated in target_capacity().)

- Prints a nested JSON schedule: day → shift → department → [staff].

# Requirements

- Python 3.8+

- Standard library only (no external packages)