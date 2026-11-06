# V001 storage review and preserved partial attempt

The initial full-file scanner verified 11 complete CSVs, including Bank March 4/5 trace files. Its per-row SQLite storage repeats full source/object hashes for each selected row, creating substantial avoidable storage overhead. It was interrupted before full qualification to introduce lossless compressed row blocks. This is an engineering storage change, not a selection/criterion change; no PASS is claimed for V001.

V001 source snapshot, source profiles, selected rows, query metadata and stdout/stderr remain intact. V002 imports only EOF-completed file profiles and their exact selected rows. The interrupted file is rescanned completely; partial rows are not mistaken for a full census. Import conservation, decompressed hashes and profile hashes are recorded in a new manifest. No old file/profile/database is overwritten.

Compression preserves each row's nanosecond time, logical source row, mapping state/error and exact raw fields. Object IDs are reconstructed from unchanged source key/row hashing. Full-file time and selection code is reused unchanged. Tests verify row fidelity, temporal selection and projection equality through storage conversion.
