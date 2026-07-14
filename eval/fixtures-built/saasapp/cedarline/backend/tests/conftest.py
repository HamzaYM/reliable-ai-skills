import os

# The isolation suite connects with the dedicated application role.
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://cedar_app:apppw@localhost:5432/cedar",
)
