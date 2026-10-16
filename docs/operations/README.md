# Orbit Data: operations

`orbit-data` is a contracts-only package. It creates no connections, reads no environment
variables, and owns no runtime resources. Operational configuration belongs to the selected
capability and provider packages.

## Selecting an implementation

Install `orbit-data` to type against the shared repository boundary. Applications that persist
data also install a capability and a provider that implement it, for example `orbit-sql` with
`orbit-sql-sqlite`, `orbit-sql-mysql`, or `orbit-sql-postgres`. A NoSQL application selects
`orbit-nosql` and an implementation such as `orbit-nosql-mongo`. These are separately installed
packages; installing this contracts package does not install them.

The implementation documentation must describe connection pool sizing, timeouts, TLS, credential
loading and rotation, transaction isolation, retry rules, shutdown behavior, and any provider
limits. Do not assume these settings are uniform merely because repositories share this API.

## Resource and transaction ownership

This package does not create a resource lifecycle. Follow the concrete provider's ownership rules
and close pools/clients during application shutdown, commonly through Core's managed resource
support. Keep repository objects returned from a `UnitOfWork` inside that context. The protocol
expects rollback for body failures and cancellation, commit on normal exit, and resource cleanup
even if commit fails. Verify concrete adapters meet those expectations and document any known
limitations.

## Scale and consistency boundaries

`Repository.list(limit=...)` is one bounded read, not a page-token API. Its ordering is undefined at
the shared contract level, and separate calls do not share a snapshot. Implementations should cap
the requested limit and document their ordering. Use a provider's bulk export or streaming feature
for large datasets; do not build an unbounded export by repeatedly calling this method and assuming
stable pagination.

The shared protocols do not promise isolation, durability, cross-provider consistency, or
exactly-once execution. Those guarantees depend on the selected backend, schema, transaction
configuration, and application retry behavior.

## Pre-release operational review

For each selected provider, verify failure recovery, pool cleanup, cancellation during active work,
transaction rollback and commit failure, backup/restore, schema migration, connection exhaustion,
and behavior under the target database version. This repository's contract tests alone cannot
provide that evidence.
