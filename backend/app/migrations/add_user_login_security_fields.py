"""Migration script to add login security fields to users table.

This script adds:
- failed_login_count: INTEGER DEFAULT 0
- locked_until: TIMESTAMP (nullable)

Run this script after updating the User model.
"""

import asyncio

from sqlalchemy import text

from app.database import engine


async def upgrade():
    """Add new columns to users table."""
    async with engine.begin() as conn:
        # Add failed_login_count column
        await conn.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS failed_login_count INTEGER NOT NULL DEFAULT 0
            """
            )
        )

        # Add locked_until column
        await conn.execute(
            text(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE
            """
            )
        )

    print("✅ Migration completed: Added login security fields to users table")


async def downgrade():
    """Remove new columns from users table."""
    async with engine.begin() as conn:
        # Drop failed_login_count column
        await conn.execute(
            text(
                """
                ALTER TABLE users
                DROP COLUMN IF EXISTS failed_login_count
            """
            )
        )

        # Drop locked_until column
        await conn.execute(
            text(
                """
                ALTER TABLE users
                DROP COLUMN IF EXISTS locked_until
            """
            )
        )

    print("⏪ Rollback completed: Removed login security fields from users table")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
