# Orbit Data: architecture and boundaries

`orbit-data` owns the shared repository and unit-of-work protocols used by data access
capabilities. It contains no database driver, object mapper, connection pool, SQL dialect, or
provider configuration, and it does not depend on Orbit Core.

```text
application module
       │ Repository[Entity, Key] / UnitOfWork
       ▼
   orbit-data                 shared repository and transaction-scope contracts
       ▲
       │ depends on contracts
   orbit-sql / orbit-nosql    capability-specific APIs and behavior
       ▲
       │ provider implementation
 orbit-sql-sqlite, -mysql, -postgres, orbit-nosql-mongo, ...
```

Providers own their SDKs, connections, credentials, error translation, and resource lifecycle.
Capabilities own interfaces that are common across providers in their domain. Core may compose
these resources through its container, but the data contracts remain independently importable.

## Repository contract

`Repository[Entity, Key]` defines `get`, `list`, `add`, `update`, and `delete`:

- `get` returns `None` when a key is absent.
- `list(limit=...)` returns a bounded tuple for one call. The contract does not define ordering,
  filtering, cursor pagination, or a snapshot across calls. It is not a bulk export API. Concrete
  implementations must document ordering and a finite accepted limit range.
- `add` inserts without mutating the caller's entity. A uniqueness conflict is translated to
  `RepositoryConflictError` without exposing backend messages or record data.
- `update` and `delete` return `False` when no existing record was affected. The contract does not
  prescribe key generation, soft-delete behavior, cascades, or retention.

The entity and key are application types. This API intentionally does not prescribe a data model,
ORM, serialization format, filtering language, schema version, or identity strategy. It also does
not promise that operations outside a unit of work are transactional.

## Unit-of-work contract

`UnitOfWork` is an async context-managed transaction boundary. A concrete implementation begins
its transaction when entering, commits on normal exit, rolls back when the body raises or is
cancelled, and releases its owned resources on every exit path. If commit fails, it should attempt
rollback and close resources while allowing the commit failure to reach the caller. Its
`__aexit__` must not suppress application exceptions.

Repositories acquired from a unit of work are scoped to that context and must not be retained after
it exits. Nested transaction behavior, isolation levels, retry policy, and durability guarantees
are provider-specific and must be described by the capability or adapter that implements them.

## Errors and sensitive information

`RepositoryConflictError` gives applications one provider-neutral signal for uniqueness conflicts.
Its public message is fixed and contains no constraint name, SQL, backend message, credential, or
entity value. Other error categories are not normalized by this package. Capability and provider
packages should define any additional portable failures they need, and preserve the original cause
only through a safe internal exception chain where their logging policy permits it.

## Current source layout

- `src/orbit_data/contracts.py`: structural protocols and shared behavioral documentation.
- `src/orbit_data/errors.py`: provider-neutral conflict exception.
- `src/orbit_data/__init__.py`: supported top-level exports.

## Compatibility and status

The project currently declares Python `>=3.11,<3.15` and is alpha. Public API compatibility is
not guaranteed before a stable release. Runtime dependencies are empty; development tools are
optional. See the repository manifest and changelog/release notes for version-specific facts.
