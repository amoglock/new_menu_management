"""initial db

Revision ID: 24168b8023e2
Revises:
Create Date: 2023-09-07 02:06:30.550072

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '24168b8023e2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('menu',
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    op.create_table('submenu',
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('menu_group', sa.Uuid(), nullable=False),
                    sa.ForeignKeyConstraint(['menu_group'], ['menu.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    op.create_table('dish',
                    sa.Column('id', sa.Uuid(), nullable=False),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('price', sa.String(), nullable=False),
                    sa.Column('submenu_group', sa.Uuid(), nullable=False),
                    sa.ForeignKeyConstraint(['submenu_group'], ['submenu.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('title')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dish')
    op.drop_table('submenu')
    op.drop_table('menu')
    # ### end Alembic commands ###
