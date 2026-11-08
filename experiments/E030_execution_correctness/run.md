# E030-R001 run record

- Planning stage XP027.
- 200 in-memory state transitions: restart, scale, reroute and rollback (50 each).
- Predicted and observed state matched exactly in 200/200 cases; the independent oracle passed. Rollback restored its supplied snapshot in 50/50 cases.
- No external action or service call occurred. There is no runnable DCE testbed in this workspace, so this is simulator evidence only.
