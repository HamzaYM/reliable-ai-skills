"""Request dependencies (auth resolves the caller's tenant)."""


def db_session():
    raise NotImplementedError


def current_tenant_id():
    raise NotImplementedError
