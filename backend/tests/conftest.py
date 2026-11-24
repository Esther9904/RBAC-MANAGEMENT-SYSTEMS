import pytest

from app.domain.store import create_store
from app.services.access_service import AccessService
from app.services.audit_log import AuditLog
from app.services.role_service import RoleService
from app.services.user_service import UserService

@pytest.fixture
def store():
    return create_store()


@pytest.fixture
def audit(store):
    return AuditLog(store)


@pytest.fixture
def access(store, audit):
    return AccessService(store, audit)

@pytest.fixture
def role_service(store):
    return RoleService(store)


@pytest.fixture
def user_service(store):
    return UserService(store)