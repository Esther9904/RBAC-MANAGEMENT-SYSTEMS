import pytest

from app.domain.store import create_store
from app.services.access_service import AccessService
from app.services.audit_log import AuditLog


@pytest.fixture
def store():
    return create_store()


@pytest.fixture
def audit(store):
    return AuditLog(store)


@pytest.fixture
def access(store, audit):
    return AccessService(store, audit)