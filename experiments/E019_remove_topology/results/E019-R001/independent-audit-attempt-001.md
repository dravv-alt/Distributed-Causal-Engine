# Independent audit attempt 001

The first audit run reached the metric comparison and stopped on `path_accuracy_when_explained`: both the independently recomputed and published values were `null` for the topology-disabled arm because it intentionally emits no explanations. The comparator attempted subtraction of `None` values. This is an audit-script handling defect, not an experiment metric or inference failure. The attempt is retained; the corrected audit handles paired null values explicitly.
