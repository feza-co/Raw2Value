"""uploaded_files table

Revision ID: 0003_uploaded_files
Revises: 0002_analysis_history
Create Date: 2026-05-03

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_uploaded_files"
down_revision = "0002_analysis_history"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "organization_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=80), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column(
            "storage_backend",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'local'"),
        ),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("public_url", sa.String(length=500), nullable=True),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_uploaded_files_user_id", "uploaded_files", ["user_id"]
    )
    op.create_index(
        "ix_uploaded_files_organization_id",
        "uploaded_files",
        ["organization_id"],
    )
    op.create_index(
        "ix_uploaded_files_kind", "uploaded_files", ["kind"]
    )
    op.create_index(
        "ix_uploaded_files_uploaded_at",
        "uploaded_files",
        [sa.text("uploaded_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_uploaded_files_uploaded_at", table_name="uploaded_files")
    op.drop_index("ix_uploaded_files_kind", table_name="uploaded_files")
    op.drop_index(
        "ix_uploaded_files_organization_id", table_name="uploaded_files"
    )
    op.drop_index("ix_uploaded_files_user_id", table_name="uploaded_files")
    op.drop_table("uploaded_files")
