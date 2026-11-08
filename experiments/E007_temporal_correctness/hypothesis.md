# E007 preregistered question and hypothesis

**Question:** Does the experimental temporal accumulator produce the same event-time windows as an independent offline oracle for identical accepted events under bounded arrival reordering, while explicitly representing missing values, a counter reset, and a late event beyond the configured bound?

**Hypothesis:** For identical accepted synthetic input records, event-time sorting and explicit masks/reset handling produce order-invariant window features; events beyond the configured lateness allowance are explicitly rejected and recorded.

**Independent variables:** arrival ordering and whether an event is inside or beyond the configured lateness bound.

**Dependent measures:** accepted/rejected event IDs and reasons; exact equality of online windows with the independent offline oracle; equality across ordered and bounded-reordered schedules; observation/value masks; missing-value count; counter delta and reset counts; start/end boundary dispositions.

**Reference:** an independently implemented offline replay in the runner, which sorts accepted records and recomputes windows without importing or calling the accumulator's result method.

**Scope and limits:** fixed synthetic nonnegative cumulative counter values with an explicit counter interpretation. This is an algorithm correctness prototype only. It does not establish real-source timestamp units, counter semantics, signal arrival delay, production streaming behavior, detector quality, or RCA effectiveness. No labels or external network inputs are used.
