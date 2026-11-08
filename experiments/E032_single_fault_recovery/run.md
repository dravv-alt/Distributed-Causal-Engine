# E032-R001 run record

- Stage XP029; 300 synthetic single-fault cases (100 per fault type).
- Controller diagnosed from noisy indicators and produced a fixed mapped action. It did not load hidden fault labels or the simulator's failure schedule.
- A generated approval flag allowed 248 in-memory action simulations and declined 52; no simulated action ran without that flag.
- 144/300 cases recovered; diagnosis accuracy was 56.7%; 104/248 approved actions were wrong for the generated fault. Logical timing was fixed by protocol (MTTD 2 ticks, successful-path MTTR 6 ticks), not measured wall-clock time.
- Independent audit passed. The approval flag was generated, not a human review; no actual service was touched.
