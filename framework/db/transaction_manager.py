"""
Transaction management for test-level rollback
"""
from typing import Optional, Callable, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy import text
from framework.db.db_client import DatabaseClient
from framework.core.logger import log


class TransactionManager:
    """Manages database transactions for test isolation"""

    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client
        self._transaction_active = False

    @contextmanager
    def transaction(self, rollback_on_error: bool = True):
        """Context manager for database transaction with automatic rollback."""
        session = self.db_client.SessionLocal()
        self._transaction_active = True
        log.debug("Transaction started")

        try:
            yield session
            if rollback_on_error:
                session.rollback()
                log.debug("Transaction rolled back (test cleanup)")
            else:
                session.commit()
                log.debug("Transaction committed")
        except Exception as e:
            session.rollback()
            log.error(f"Transaction rolled back due to error: {str(e)}")
            raise
        finally:
            session.close()
            self._transaction_active = False
            log.debug("Transaction closed")

    @contextmanager
    def savepoint(self, name: str = "test_savepoint", session: Optional[Session] = None):
        """Create a savepoint within an existing session."""
        owns_session = session is None
        active_session = session or self.db_client.SessionLocal()
        try:
            active_session.execute(text(f"SAVEPOINT {name}"))
            log.debug(f"Savepoint created: {name}")
            yield active_session
            active_session.execute(text(f"RELEASE SAVEPOINT {name}"))
            log.debug(f"Savepoint released: {name}")
        except Exception:
            active_session.execute(text(f"ROLLBACK TO SAVEPOINT {name}"))
            log.debug(f"Rolled back to savepoint: {name}")
            raise
        finally:
            if owns_session:
                active_session.close()


def with_transaction_rollback(db_client: DatabaseClient):
    """Decorator to wrap test function with transaction rollback."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            manager = TransactionManager(db_client)
            with manager.transaction(rollback_on_error=True):
                return func(*args, **kwargs)
        return wrapper
    return decorator
