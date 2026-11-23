"""stripe pago unico CU-027 CU-037 CU-039

Revision ID: c7d8e9f0a1b2
Revises: f1a2b3c4d5e6
Create Date: 2026-11-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Pago (CU-027): referencias de Stripe sin alterar el enum de método/estado.
    op.add_column(
        'pago',
        sa.Column('proveedor', sa.String(length=20), server_default='manual', nullable=False),
    )
    for column in ('idtransaccion', 'paymentintentid', 'estadopasarela'):
        op.add_column('pago', sa.Column(column, sa.String(length=255), nullable=True))
    op.alter_column('pago', 'estadopasarela', type_=sa.String(length=40), existing_type=sa.String(length=255))
    op.create_index('ix_pago_idtransaccion', 'pago', ['idtransaccion'])

    # Cobro (CU-039): mismos campos para el checkout de facturas.
    op.add_column(
        'cobro',
        sa.Column('proveedor', sa.String(length=20), server_default='manual', nullable=False),
    )
    op.add_column('cobro', sa.Column('idtransaccion', sa.String(length=255), nullable=True))
    op.add_column('cobro', sa.Column('paymentintentid', sa.String(length=255), nullable=True))
    op.add_column('cobro', sa.Column('estadopasarela', sa.String(length=40), nullable=True))
    op.create_index('ix_cobro_idtransaccion', 'cobro', ['idtransaccion'])

    # Idempotencia del webhook: un evento de Stripe se procesa una sola vez.
    op.create_table(
        'stripeevento',
        sa.Column('idevento', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('eventoid', sa.String(length=255), nullable=False),
        sa.Column('tipo', sa.String(length=100), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('referencia', sa.String(length=50), nullable=True),
        sa.Column('procesadoen', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('idevento'),
    )
    op.create_index('ix_stripeevento_eventoid', 'stripeevento', ['eventoid'], unique=True)
    op.create_index('ix_stripeevento_tenant_id', 'stripeevento', ['tenant_id'])


def downgrade() -> None:
    op.drop_index('ix_stripeevento_tenant_id', table_name='stripeevento')
    op.drop_index('ix_stripeevento_eventoid', table_name='stripeevento')
    op.drop_table('stripeevento')
    op.drop_index('ix_cobro_idtransaccion', table_name='cobro')
    for column in ('estadopasarela', 'paymentintentid', 'idtransaccion', 'proveedor'):
        op.drop_column('cobro', column)
    op.drop_index('ix_pago_idtransaccion', table_name='pago')
    for column in ('estadopasarela', 'paymentintentid', 'idtransaccion', 'proveedor'):
        op.drop_column('pago', column)
