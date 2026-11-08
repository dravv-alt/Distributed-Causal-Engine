# E033-R001 run record

- Planning stage XP030; 300 generated cascades with the declared DB→B→A→retry chain.
- Propagation-aware diagnosis selected the upstream database node in all cases and the correct generated path in all cases. One repair action produced stable recovery in the simulator in 300/300 cases.
- Independent symptom treatment cleared symptoms at the first simulated check but left the root fault active; recovery was unstable in 300/300 by check three.
- Independent graph/transition audit passed. All actions/effects were simulated; no retry storm or service was run.
