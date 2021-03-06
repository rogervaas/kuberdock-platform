
# KuberDock - is a platform that allows users to run applications using Docker
# container images and create SaaS / PaaS based on these applications.
# Copyright (C) 2017 Cloud Linux INC
#
# This file is part of KuberDock.
#
# KuberDock is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# KuberDock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KuberDock; if not, see <http://www.gnu.org/licenses/>.

"""Move timezone setting to its own column

Revision ID: 4fbcae87c090
Revises: 28b23145af40
Create Date: 2015-11-05 16:54:57.028108

"""

# revision identifiers, used by Alembic.
revision = '4fbcae87c090'
down_revision = '28b23145af40'

import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DEFAULT_TIMEZONE = 'UTC'

Session = sessionmaker()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True,
                   nullable=False)
    settings = sa.Column(sa.Text)
    timezone = sa.Column(sa.String(64), nullable=False,
                         default=DEFAULT_TIMEZONE,
                         server_default=DEFAULT_TIMEZONE)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('timezone', sa.String(length=64), server_default='UTC', nullable=False))
    ### end Alembic commands ###
    key = 'timezone'
    for user in session.query(User):
        settings = json.loads(user.settings) if user.settings else {}
        if key in settings:
            user.timezone = settings[key]
            del settings[key]
            user.settings = json.dumps(settings)
        else:
            user.timezone = DEFAULT_TIMEZONE
    session.commit()


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'timezone')
    ### end Alembic commands ###
