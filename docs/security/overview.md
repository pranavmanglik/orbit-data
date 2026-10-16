# Orbit Data: security

`orbit-data` is a type-contract package. It does not authenticate users, access databases, hold
credentials, or process records at runtime. Security controls for connections and stored data belong
to the selected provider and deployment.

## Contract-level guidance

- Treat entities and keys as application data. Avoid placing credentials, access tokens, or other
  secrets in repository keys or exception messages.
- Do not expose raw provider errors through a public API. Translate uniqueness violations to
  `RepositoryConflictError`; its fixed message avoids leaking constraint names and record values.
- Keep repositories acquired from a `UnitOfWork` within the transaction scope. Use the concrete
  provider's documented cleanup path on normal exit, rollback, cancellation, and commit failure.
- Do not infer authorization from repository access. Applications must enforce tenant and user
  access before reading or changing records; these protocols carry no principal or policy context.

## Provider and deployment controls

Review the adapter's authentication mode, least-privilege database role, TLS and certificate
verification, secret storage and rotation, query logging, pool limits, transaction isolation,
backup encryption, retention, and recovery controls. Ensure application logs do not include SQL
parameters or sensitive entity fields. These settings are provider-specific and are not configured
by `orbit-data`.

## Reporting and scope

Follow the repository [security policy](../../SECURITY.md) for private vulnerability reporting.
This page records the scope of the shared contracts; it is not an audit or certification of any
database adapter or deployment.
