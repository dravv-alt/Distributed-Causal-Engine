# E018 decision

**Disposition:** synthetic ablation is inconclusive about neural-branch value; application-level contribution remains UNKNOWN.

Removing the neural feature increased Top-1 by 1.3 percentage points in this synthetic sample, but the paired 95% interval ranged from -1.5 to +4.0 points. MRR changed by +0.0108 (interval -0.0049 to +0.0261). The fixed softmax rank calibration diagnostics were also lower without neural input, but these are not calibrated application probabilities.

This generated result does not justify removing neural evidence from DCE. Continue to XP016 as a separately registered synthetic ablation; preserve the real-data contribution as unknown.
