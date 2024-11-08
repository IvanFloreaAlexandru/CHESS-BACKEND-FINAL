"""Achievements & others

Revision ID: efef00cc68fb
Revises: 82825ca3aba7
Create Date: 2024-10-02 16:11:38.408449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efef00cc68fb'
down_revision: Union[str, None] = '82825ca3aba7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'achievement_keeper', ['Achievement_Keeper_Id'])
    op.create_unique_constraint(None, 'achievements', ['achievement_id'])
    op.drop_column('user_statistics', 'elo')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_statistics', sa.Column('elo', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'achievements', type_='unique')
    op.drop_constraint(None, 'achievement_keeper', type_='unique')
    # ### end Alembic commands ###
