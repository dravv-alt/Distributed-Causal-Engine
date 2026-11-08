# E029-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP026. Generate 600 cases balanced across CPU saturation, database saturation, and network-path bottleneck, seed 29026. Make 70% diagnoses correct, 20% wrong, and 10% `UNKNOWN`; labels for true mechanism and oracle action are evaluator-only.

Fixed recommendation map: CPU saturation→scale service; DB saturation→repair database; network bottleneck→reroute traffic. Unknown diagnosis causes abstention. Report action-oracle consistency on covered diagnoses, correctness against true mechanism, abstention, and false-recommendation rate on unknown cases. No execution.
