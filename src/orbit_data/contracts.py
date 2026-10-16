# Copyright 2026-present Orbit Contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Provider-neutral repository and transaction-scope contracts for Orbit data packages."""

from __future__ import annotations

from types import TracebackType
from typing import Protocol, TypeVar, runtime_checkable

EntityT = TypeVar("EntityT")
KeyT = TypeVar("KeyT", contravariant=True)


@runtime_checkable
class Repository(Protocol[EntityT, KeyT]):
    """Typed CRUD boundary for one entity type and its application-defined key type.

    Implementations return ``None`` from ``get`` when a key is absent. ``update`` and ``delete``
    return whether an existing record was affected. ``list`` is a single bounded read; this
    protocol does not define ordering, filtering, a continuation token, or a snapshot spanning
    multiple calls. It is therefore not a bulk-export or stable-pagination contract.

    Implementations translate provider-specific uniqueness conflicts to
    :class:`orbit_data.RepositoryConflictError` without including provider messages, query text,
    credentials, or record values in the public exception. Other failures remain implementation
    specific unless a capability package defines a shared error contract.

    Repository instances obtained from a :class:`UnitOfWork` are scoped to that unit of work and
    must not be retained or used after its context exits. This protocol does not promise that
    operations outside a unit of work are transactional.
    """

    async def get(self, key: KeyT) -> EntityT | None:
        """Return one entity by key, or ``None`` when it does not exist.

        An implementation must not turn a missing row into a provider-specific exception. The
        entity is an application value; callers should not depend on a live database model or
        connection being attached to it.
        """

    async def list(self, *, limit: int = 100) -> tuple[EntityT, ...]:
        """Return at most ``limit`` entities in one bounded read.

        ``limit`` must be positive; implementations should also enforce a documented finite
        maximum. Ordering is provider or implementation defined unless the concrete repository
        documents a stronger guarantee. This method does not provide pagination, filtering, or a
        consistent snapshot across separate calls. Use provider-specific bulk tools for exports.
        """

    async def add(self, entity: EntityT) -> None:
        """Insert an entity without mutating the supplied object.

        A uniqueness conflict must be surfaced as :class:`RepositoryConflictError`. The contract
        does not prescribe key generation or whether an entity's key must already exist.
        """

    async def update(self, entity: EntityT) -> bool:
        """Replace the stored entity with the same key; return whether it existed.

        ``False`` means no matching entity was changed. Implementations should report uniqueness
        conflicts through :class:`RepositoryConflictError`, without leaking backend details.
        """

    async def delete(self, key: KeyT) -> bool:
        """Delete an entity by key and report whether one was present.

        ``False`` means no matching entity was deleted. The method does not imply soft deletion,
        cascading behavior, or retention guarantees; those belong to the concrete implementation.
        """


@runtime_checkable
class UnitOfWork(Protocol):
    """Async transaction scope that commits on normal exit and rolls back on failure.

    Implementations must include cancellation in the failure path and release all owned resources
    before leaving the context. If commit fails, implementations should attempt rollback and still
    close owned resources; the commit failure remains visible to the caller. Repository objects
    obtained from a unit of work must not outlive it. Nested-unit-of-work behavior and isolation
    level are implementation-defined and must be documented by the concrete package.
    """

    async def __aenter__(self) -> UnitOfWork:
        """Begin the transaction and return its unit-of-work facade."""

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Commit on success or roll back on any exception, including cancellation.

        Return ``False`` or ``None`` so the original exception propagates. Returning ``True`` would
        suppress an application failure and is outside this contract. Resource cleanup must happen
        on normal exit, rollback, cancellation, and commit failure.
        """


__all__ = ["Repository", "UnitOfWork"]
