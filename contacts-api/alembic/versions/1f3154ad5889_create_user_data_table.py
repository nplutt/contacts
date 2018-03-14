"""create user data table

Revision ID: 1f3154ad5889
Revises: 48b0aff7efc6
Create Date: 2018-03-03 18:26:28.396329

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import sync_trigger

# revision identifiers, used by Alembic.
revision = '1f3154ad5889'
down_revision = '48b0aff7efc6'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    op.create_table(
        'user_data',
        sa.Column('data_id', postgresql.UUID(), nullable=False),
        sa.Column('field_type', sa.String(), nullable=False),
        sa.Column('field_data', sa.String(), nullable=False),
        sa.Column('search_vector', TSVectorType('field_data'), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('add_name', sa.String(), nullable=True),
        sa.Column('add_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_maintenance_name', sa.String(), nullable=True),
        sa.Column('last_maintenance_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('data_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE')
    )

    sync_trigger(conn=conn,
                 table_name='user_data',
                 tsvector_column='search_vector',
                 indexed_columns=['field_data'])


def downgrade():
    op.drop_table('user_data')
