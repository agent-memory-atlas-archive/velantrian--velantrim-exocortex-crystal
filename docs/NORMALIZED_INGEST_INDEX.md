# Normalized ingest index completeness

The normalized index is disposable derived routing data. It does not admit evidence, establish semantic equivalence, or promote a fact. Returned candidates must still pass decryption and exact claim normalization. Explicit caller-supplied fact IDs retain their existing path.

Schema version 4 adds a versioned completeness record and invalidation triggers. A fast negative lookup is usable only when the table/index/trigger structure is valid, the protocol version matches, and covered generation equals current generation. Otherwise the resolver performs the read-only exact scan over eligible Validated, unrestricted auto-ID facts. A resolver holds one SQLite snapshot across its completeness and candidate reads.

Official writers capture completeness under their write lock and maintain touched mappings in the same transaction. Direct SQL writes invalidate coverage. A full rebuild is transactional and publishes covered generation last; a failed rebuild cannot publish a complete partial index. A cache-maintenance failure does not authorize or imply a primary fact write.

Rebuild after ingest occurs only after a successful duplicate write or a post-Guardian/TruthGate claim-bound ESM CAS. The resolver does not rebuild on query. Review-decision and erasure paths maintain their mappings inside their owning transactions.

Validation: `tests/test_normalized_ingest_index.py` and `tests/test_dedup.py` cover migration, damaged structures, exact identity, encryption, concurrency, rollback, gate failure and outbox boundaries. Full CI and the existing coverage/security gates remain required. This change does not close reserved-ID squatting, terminal-state import handling, or unrelated audit/HMAC findings.
