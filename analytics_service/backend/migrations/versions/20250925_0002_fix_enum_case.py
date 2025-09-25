"""Fix enum case mismatch

Revision ID: 20250925_0002
Revises: 20240924_0001
Create Date: 2025-09-25 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20250925_0002'
down_revision: Union[str, None] = '20240924_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # First, update existing data to use lowercase values
    op.execute("UPDATE request_events SET status = 'success' WHERE status = 'SUCCESS'")
    op.execute("UPDATE request_events SET status = 'error' WHERE status = 'ERROR'")
    op.execute("UPDATE request_events SET status = 'partial' WHERE status = 'PARTIAL'")
    
    # Drop the old enum type
    op.execute("ALTER TABLE request_events ALTER COLUMN status TYPE VARCHAR(20)")
    op.execute("DROP TYPE IF EXISTS request_status")
    
    # Create new enum type with lowercase values
    op.execute("CREATE TYPE request_status AS ENUM ('success', 'error', 'partial')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE request_events ALTER COLUMN status TYPE request_status USING status::request_status")


def downgrade() -> None:
    # Update data back to uppercase
    op.execute("UPDATE request_events SET status = 'SUCCESS' WHERE status = 'success'")
    op.execute("UPDATE request_events SET status = 'ERROR' WHERE status = 'error'")
    op.execute("UPDATE request_events SET status = 'PARTIAL' WHERE status = 'partial'")
    
    # Drop the new enum type
    op.execute("ALTER TABLE request_events ALTER COLUMN status TYPE VARCHAR(20)")
    op.execute("DROP TYPE IF EXISTS request_status")
    
    # Recreate old enum type with uppercase values
    op.execute("CREATE TYPE request_status AS ENUM ('SUCCESS', 'ERROR', 'PARTIAL')")
    
    # Convert column back to enum type
    op.execute("ALTER TABLE request_events ALTER COLUMN status TYPE request_status USING status::request_status")