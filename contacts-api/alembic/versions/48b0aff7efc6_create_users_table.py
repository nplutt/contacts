"""create users table

Revision ID: 48b0aff7efc6
Revises: 
Create Date: 2018-03-03 18:15:51.747871

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '48b0aff7efc6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', postgresql.UUID(), unique=True, nullable=False),
        sa.Column('email_address', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('add_name', sa.String(), nullable=True),
        sa.Column('add_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_maintenance_name', sa.String(), nullable=True),
        sa.Column('last_maintenance_date', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('email_address', 'first_name', 'last_name')
    )


def downgrade():
    op.drop_table('users')
