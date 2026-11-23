"""tablas sprint4 facturacion cuotas

Revision ID: f1a2b3c4d5e6
Revises: 83c5ca311fb6
Create Date: 2026-11-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '83c5ca311fb6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    # Si la tabla 'plan' no existe (base de datos nueva), crearla previamente
    if 'plan' not in tables:
        op.create_table(
            'plan',
            sa.Column('idplan', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('codigo', sa.String(length=32), nullable=False),
            sa.Column('nombre', sa.String(length=100), nullable=False),
            sa.Column('descripcion', sa.Text(), nullable=True),
            sa.Column('preciomensual', sa.Numeric(12, 2), server_default='0.00', nullable=False),
            sa.Column('precioanual', sa.Numeric(12, 2), server_default='0.00', nullable=False),
            sa.Column('moneda', sa.String(length=3), server_default='USD', nullable=False),
            sa.Column('limiteusuarios', sa.Integer(), nullable=True),
            sa.Column('limiteunidades', sa.Integer(), nullable=True),
            sa.Column('limitereportesmes', sa.Integer(), nullable=True),
            sa.Column('limitealmacenamientomb', sa.Integer(), nullable=True),
            sa.Column('diastrial', sa.Integer(), server_default='0', nullable=False),
            sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
            sa.Column('creadoen', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('actualizadoen', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('idplan'),
            sa.UniqueConstraint('codigo', name='uq_plan_codigo')
        )
        op.create_index('ix_plan_codigo', 'plan', ['codigo'])

    # Si la tabla 'suscripcion' no existe (base de datos nueva), crearla previamente para resolver FK en factura
    if 'suscripcion' not in tables:
        estado_suscripcion_enum = sa.Enum(
            'trial', 'activa', 'vencida', 'suspendida', 'cancelada',
            name='estado_suscripcion_enum'
        )
        existing_enums = [e['name'] for e in insp.get_enums()] if hasattr(insp, 'get_enums') else []
        if 'estado_suscripcion_enum' not in existing_enums:
            estado_suscripcion_enum.create(bind, checkfirst=True)

        op.create_table(
            'suscripcion',
            sa.Column('idsuscripcion', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('idtenant', sa.Integer(), sa.ForeignKey('tenant.idtenant'), nullable=False),
            sa.Column('idplan', sa.Integer(), sa.ForeignKey('plan.idplan'), nullable=False),
            sa.Column('estado', estado_suscripcion_enum, server_default='trial', nullable=False),
            sa.Column('fechainicio', sa.DateTime(), nullable=False),
            sa.Column('fechafin', sa.DateTime(), nullable=False),
            sa.Column('renovacionautomatica', sa.Boolean(), server_default='false', nullable=False),
            sa.Column('motivocancelacion', sa.Text(), nullable=True),
            sa.Column('creadoen', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('actualizadoen', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('idsuscripcion')
        )
        op.create_index('ix_suscripcion_idtenant', 'suscripcion', ['idtenant'])
        op.create_index('ix_suscripcion_idplan', 'suscripcion', ['idplan'])
        op.create_index('ix_suscripcion_fechafin', 'suscripcion', ['fechafin'])

    op.create_table(
        'usoplan',
        sa.Column('iduso', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('idtenant', sa.Integer(), sa.ForeignKey('tenant.idtenant'), nullable=False),
        sa.Column('periodo', sa.String(length=7), nullable=False),
        sa.Column('reportesgenerados', sa.Integer(), server_default='0', nullable=False),
        sa.Column('unidadesregistradas', sa.Integer(), server_default='0', nullable=False),
        sa.Column('usuariosactivos', sa.Integer(), server_default='0', nullable=False),
        sa.Column('actualizadoen', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('iduso'),
        sa.UniqueConstraint('idtenant', 'periodo', name='uq_usoplan_tenant_periodo'),
    )
    op.create_index('ix_usoplan_idtenant', 'usoplan', ['idtenant'])

    op.create_table(
        'factura',
        sa.Column('idfactura', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('idtenant', sa.Integer(), sa.ForeignKey('tenant.idtenant'), nullable=False),
        sa.Column('idsuscripcion', sa.Integer(), sa.ForeignKey('suscripcion.idsuscripcion'), nullable=True),
        sa.Column('numero', sa.String(length=32), nullable=False),
        sa.Column('fechaemision', sa.DateTime(), nullable=False),
        sa.Column('fechavencimiento', sa.DateTime(), nullable=False),
        sa.Column('monto', sa.Numeric(12, 2), nullable=False),
        sa.Column('moneda', sa.String(length=3), server_default='USD', nullable=False),
        sa.Column('estado', sa.String(length=20), server_default='pendiente', nullable=False),
        sa.PrimaryKeyConstraint('idfactura'),
        sa.UniqueConstraint('idtenant', 'numero', name='uq_factura_tenant_numero'),
    )
    op.create_index('ix_factura_idtenant', 'factura', ['idtenant'])

    op.create_table(
        'facturadetalle',
        sa.Column('idfacturadetalle', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('idfactura', sa.Integer(), sa.ForeignKey('factura.idfactura'), nullable=False),
        sa.Column('concepto', sa.String(length=200), nullable=False),
        sa.Column('cantidad', sa.Integer(), server_default='1', nullable=False),
        sa.Column('preciounitario', sa.Numeric(12, 2), nullable=False),
        sa.Column('subtotal', sa.Numeric(12, 2), nullable=False),
        sa.PrimaryKeyConstraint('idfacturadetalle'),
    )

    op.create_table(
        'cobro',
        sa.Column('idcobro', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('idfactura', sa.Integer(), sa.ForeignKey('factura.idfactura'), nullable=False),
        sa.Column('fechacobro', sa.DateTime(), nullable=False),
        sa.Column('monto', sa.Numeric(12, 2), nullable=False),
        sa.Column('metodopago', sa.String(length=40), nullable=False),
        sa.Column('referencia', sa.String(length=100), nullable=True),
        sa.Column('estado', sa.String(length=20), server_default='completado', nullable=False),
        sa.PrimaryKeyConstraint('idcobro'),
    )

    # Unicidad física para evitar que una unidad se asigne dos veces (P5).
    for table, constraint in (
        ('ventaunidad', 'uq_ventaunidad_idunidad'),
        ('devolucionunidad', 'uq_devolucionunidad_idunidad'),
        ('garantiaunidad', 'uq_garantiaunidad_idunidad'),
    ):
        op.create_unique_constraint(constraint, table, ['idunidad'])


def downgrade() -> None:
    for table, constraint in (
        ('garantiaunidad', 'uq_garantiaunidad_idunidad'),
        ('devolucionunidad', 'uq_devolucionunidad_idunidad'),
        ('ventaunidad', 'uq_ventaunidad_idunidad'),
    ):
        op.drop_unique_constraint(constraint, table)
    op.drop_table('cobro')
    op.drop_table('facturadetalle')
    op.drop_index('ix_factura_idtenant', table_name='factura')
    op.drop_table('factura')
    op.drop_index('ix_usoplan_idtenant', table_name='usoplan')
    op.drop_table('usoplan')

    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()
    if 'suscripcion' in tables:
        op.drop_index('ix_suscripcion_fechafin', table_name='suscripcion')
        op.drop_index('ix_suscripcion_idplan', table_name='suscripcion')
        op.drop_index('ix_suscripcion_idtenant', table_name='suscripcion')
        op.drop_table('suscripcion')
    if 'plan' in tables:
        op.drop_index('ix_plan_codigo', table_name='plan')
        op.drop_table('plan')
