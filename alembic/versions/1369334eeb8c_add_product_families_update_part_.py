"""add product_families, update part_numbers and lots

Revision ID: 1369334eeb8c
Revises: 92ebbaf4dd87
Create Date: 2026-09-12 13:19:19.506426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1369334eeb8c'
down_revision: Union[str, Sequence[str], None] = '92ebbaf4dd87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'product_families',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('proposed_by', sa.String(), sa.ForeignKey('users.username'), nullable=False),
        sa.Column('approved_by', sa.String(), sa.ForeignKey('users.username'), nullable=True),
        sa.PrimaryKeyConstraint('name')
    )
    op.create_index(op.f('ix_product_families_name'), 'product_families', ['name'], unique=False)

    with op.batch_alter_table('part_numbers') as batch_op:
        batch_op.add_column(sa.Column('family_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('status', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('proposed_by', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('approved_by', sa.String(), nullable=True))

    with op.batch_alter_table('lots') as batch_op:
        batch_op.add_column(sa.Column('ncr_number', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('me_approved_by', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('qe_approved_by', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('lots') as batch_op:
        batch_op.drop_column('qe_approved_by')
        batch_op.drop_column('me_approved_by')
        batch_op.drop_column('ncr_number')

    with op.batch_alter_table('part_numbers') as batch_op:
        batch_op.drop_column('approved_by')
        batch_op.drop_column('proposed_by')
        batch_op.drop_column('status')
        batch_op.drop_column('family_name')

    op.drop_index(op.f('ix_product_families_name'), table_name='product_families')
    op.drop_table('product_families')