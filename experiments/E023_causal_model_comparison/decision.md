# E023 decision

**Disposition:** measured-confounder adjustment worked in the specified synthetic linear models; identification assumptions remain unverified for real data.

The explicit adjusted model achieved 100% causal-link accuracy (Wilson interval 99.36–100.0%) and intervention-reference effect RMSE 0.125. The observational model had 50% path accuracy, 100% false-causal calls among common-cause cases, and RMSE 0.548. Omitting U changed the link decision in 300/600 cases and shifted estimates by a mean absolute 0.413.

These outcomes follow from the generator's linear equations, observed U, and matched potential outcomes. They do not validate an adjustment set, structural model, or causal effect in DCE. Proceed to XP021 with a separate preregistered counterfactual prediction comparison.
