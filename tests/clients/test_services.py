import pytest
from uuid import uuid4


# Service layer tests are covered by router integration tests
# The router tests call create_client, read_client, update_client, delete_client
# via the HTTP endpoints, which effectively tests the service layer
