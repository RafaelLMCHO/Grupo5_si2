"""agregar_tablas_backup_tenant

Revision ID: 83c5ca311fb6
Revises: 4eaeaf39d7a4
Create Date: 2026-10-06 00:32:37.474512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83c5ca311fb6'
down_revision: Union[str, Sequence[str], None] = '4eaeaf39d7a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear tablas para copias de seguridad por tenant (CU-001)."""
    op.create_table(
        'tenant_backup',
        sa.Column('idbackup', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('idtenant', sa.Integer(), nullable=False),
        sa.Column('idusuario_creador', sa.Integer(), nullable=False),
        sa.Column('nombre_archivo', sa.String(length=255), nullable=False),
        sa.Column('cloud_storage', sa.String(length=50), nullable=False, server_default='supabase'),
        sa.Column('cloud_path', sa.String(length=500), nullable=False),
        sa.Column('peso_bytes', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('checksum_sha256', sa.String(length=64), nullable=True),
        sa.Column('estado', sa.String(length=30), nullable=False, server_default='PENDIENTE'),
        sa.Column('mensaje_error', sa.Text(), nullable=True),
        sa.Column('total_registros', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('fechacreacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['idtenant'], ['tenant.idtenant'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['idusuario_creador'], ['usuario.idusuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('idbackup')
    )

    op.create_table(
        'tenant_backup_schedule',
        sa.Column('idschedule', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('idtenant', sa.Integer(), nullable=False),
        sa.Column('idusuario_creador', sa.Integer(), nullable=False),
        sa.Column('fecha_hora_programada', sa.DateTime(), nullable=False),
        sa.Column('frecuencia', sa.String(length=20), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='PROGRAMADO'),
        sa.Column('ultimo_ejecutado', sa.DateTime(), nullable=True),
        sa.Column('proxima_ejecucion', sa.DateTime(), nullable=True),
        sa.Column('mensaje_resultado', sa.Text(), nullable=True),
        sa.Column('fechacreacion', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['idtenant'], ['tenant.idtenant'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['idusuario_creador'], ['usuario.idusuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('idschedule')
    )


def downgrade() -> None:
    """Eliminar tablas de backup."""
    op.drop_table('tenant_backup_schedule')
    op.drop_table('tenant_backup')
