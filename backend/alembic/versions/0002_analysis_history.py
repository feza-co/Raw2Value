"""analysis_history table

Revision ID: 0002_analysis_history
Revises: 0001_initial
Create Date: 2026-05-03

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_analysis_history"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, primary_key=True),
        sa.Column("request_id", sa.String(length=40), nullable=False, unique=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        # Input snapshot
        sa.Column("raw_material", sa.String(length=30), nullable=False),
        sa.Column("tonnage", sa.Numeric(10, 2), nullable=False),
        sa.Column("quality", sa.String(length=10), nullable=False),
        sa.Column("origin_city", sa.String(length=100), nullable=False),
        sa.Column("target_country", sa.String(length=2), nullable=False),
        sa.Column("target_city", sa.String(length=100), nullable=True),
        sa.Column("transport_mode", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=30), nullable=False),
        sa.Column("input_mode", sa.String(length=20), nullable=False),
        sa.Column(
            "fx_scenario_pct",
            sa.Numeric(5, 4),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "cost_scenario_pct",
            sa.Numeric(5, 4),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("payload_json", postgresql.JSONB(), nullable=False),
        # Output snapshot
        sa.Column("recommended_route", sa.String(length=80), nullable=False),
        sa.Column("expected_profit_try", sa.Numeric(14, 2), nullable=True),
        sa.Column("value_uplift_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("co2_kg", sa.Numeric(12, 2), nullable=True),
        sa.Column("confidence_overall", sa.Numeric(5, 2), nullable=True),
        sa.Column("response_json", postgresql.JSONB(), nullable=False),
        # FX snapshot
        sa.Column("usd_try_at_call", sa.Numeric(8, 4), nullable=True),
        sa.Column("eur_try_at_call", sa.Numeric(8, 4), nullable=True),
        sa.Column("fx_last_updated", sa.DateTime(timezone=True), nullable=True),
        # Performans
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("model_version", sa.String(length=20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_analysis_history_request_id", "analysis_history", ["request_id"], unique=True)
    op.create_index("ix_analysis_history_user_id", "analysis_history", ["user_id"])
    op.create_index("ix_analysis_history_organization_id", "analysis_history", ["organization_id"])
    op.create_index("ix_analysis_history_raw_material", "analysis_history", ["raw_material"])
    op.create_index("ix_analysis_history_recommended_route", "analysis_history", ["recommended_route"])
    op.create_index(
        "ix_analysis_history_created_at_desc",
        "analysis_history",
        [sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_index("ix_analysis_history_created_at_desc", table_name="analysis_history")
    op.drop_index("ix_analysis_history_recommended_route", table_name="analysis_history")
    op.drop_index("ix_analysis_history_raw_material", table_name="analysis_history")
    op.drop_index("ix_analysis_history_organization_id", table_name="analysis_history")
    op.drop_index("ix_analysis_history_user_id", table_name="analysis_history")
    op.drop_index("ix_analysis_history_request_id", table_name="analysis_history")
    op.drop_table("analysis_history")
