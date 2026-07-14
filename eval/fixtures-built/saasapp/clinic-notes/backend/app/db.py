"""Engine and org resolution stubs."""


class _Engine:
    def begin(self):
        raise NotImplementedError("no database in this checkout")


engine = _Engine()


def resolve_org(user):
    return user.get("org_id")
