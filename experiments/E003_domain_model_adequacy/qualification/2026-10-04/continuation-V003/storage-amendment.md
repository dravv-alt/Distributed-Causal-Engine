# Storage engineering amendment before V002

The frozen semantic question, windows, full-file census, no-fabrication rule and Aâ€“H gate criteria are unchanged. V002 changes physical storage from independently compressed per-row records with repeated metadata to compressed blocks (up to 1024 records or 4 MiB raw per block). Source headers/paths remain in a separate catalog. This reduces storage and preserves exact strings/source pointers and mapping outcomes.

Complete V001 profiles are inherited only when their associated selected rows conserve the recorded counts. Incomplete files are rescanned from the beginning. Original profiles/inputs are identified by hashes and EOF CRC verification; no samples are substituted for complete files. The V002 snapshot and provenance include both storage implementations and the inheritance chain.
