"""create database user

Revision ID: b87a9f91244d
Revises: 1f3154ad5889
Create Date: 2018-03-03 18:59:29.125400

"""
from alembic import op
from os import getenv


# revision identifiers, used by Alembic.
revision = 'b87a9f91244d'
down_revision = '1f3154ad5889'
branch_labels = None
depends_on = None

DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")


def upgrade():
    op.execute("CREATE USER {} WITH PASSWORD '{}';"
               .format(DB_USER, DB_PASSWORD))
    op.execute("GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users, user_data TO {};"
               .format(DB_USER))


def downgrade():
    op.execute("REVOKE SELECT, INSERT, UPDATE, DELETE ON TABLE users, user_data FROM {};"
               .format(DB_USER))
    op.execute("DROP USER {};".format(DB_USER))
