"""initial schema: users, organizations, profiles

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-03

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # gen_random_uuid() için pgcrypto extension'ı zorunlu.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("organization_type", sa.String(length=50), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column(
            "country", sa.String(length=2), nullable=False, server_default=sa.text("'TR'")
        ),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column(
            "can_supply_raw_material",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "can_process_material",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "can_buy_material", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "can_export", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "has_storage", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column(
            "has_transport_capacity",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_organizations_can_supply_raw_material",
        "organizations",
        ["can_supply_raw_material"],
        postgresql_where=sa.text("can_supply_raw_material = TRUE"),
    )
    op.create_index(
        "ix_organizations_can_process_material",
        "organizations",
        ["can_process_material"],
        postgresql_where=sa.text("can_process_material = TRUE"),
    )
    op.create_index(
        "ix_organizations_can_buy_material",
        "organizations",
        ["can_buy_material"],
        postgresql_where=sa.text("can_buy_material = TRUE"),
    )
    op.create_index("ix_organizations_lat_lon", "organizations", ["lat", "lon"])

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "role", sa.String(length=20), nullable=False, server_default=sa.text("'user'")
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "producer_profiles",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "raw_materials",
            postgresql.ARRAY(sa.String(length=50)),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
        sa.Column("capacity_ton_year", sa.Integer(), nullable=True),
        sa.Column(
            "quality_grades",
            postgresql.ARRAY(sa.String(length=2)),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
    )

    op.create_table(
        "processor_profiles",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "processing_routes",
            postgresql.ARRAY(sa.String(length=50)),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
        sa.Column("capacity_ton_year", sa.Integer(), nullable=True),
        sa.Column(
            "certifications",
            postgresql.ARRAY(sa.String(length=50)),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
        sa.Column("unit_cost_try_per_ton", sa.Numeric(10, 2), nullable=True),
    )

    op.create_table(
        "buyer_profiles",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "product_interests",
            postgresql.ARRAY(sa.String(length=50)),
            nullable=False,
            server_default=sa.text("'{}'::varchar[]"),
        ),
        sa.Column("payment_terms_days", sa.Integer(), nullable=True),
        sa.Column("credit_score", sa.Numeric(3, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("buyer_profiles")
    op.drop_table("processor_profiles")
    op.drop_table("producer_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.drop_index("ix_organizations_lat_lon", table_name="organizations")
    op.drop_index("ix_organizations_can_buy_material", table_name="organizations")
    op.drop_index("ix_organizations_can_process_material", table_name="organizations")
    op.drop_index("ix_organizations_can_supply_raw_material", table_name="organizations")
    op.drop_table("organizations")
