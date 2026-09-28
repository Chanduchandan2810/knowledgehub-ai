import pytest
import os

pytestmark = pytest.mark.asyncio

async def skip_if_no_db_auth_user():
    # Helper to avoid the tests failing due to strict FK on auth.users which can't be populated
    pass

