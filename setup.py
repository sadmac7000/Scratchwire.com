# -*- coding: utf-8 -*-
# Copyright © 2014 Casey Dahlin
#
# this file is part of foobar.
#
# foobar is free software: you can redistribute it and/or modify
# it under the terms of the gnu general public license as published by
# the free software foundation, either version 3 of the license, or
# (at your option) any later version.
#
# foobar is distributed in the hope that it will be useful,
# but without any warranty; without even the implied warranty of
# merchantability or fitness for a particular purpose.  see the
# gnu general public license for more details.
#
# you should have received a copy of the gnu general public license
# along with foobar.  if not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
setup(
        name='ScratchWire.com',
        version='0.1',
        long_description=__doc__,
        packages=['scratchwire'],
        include_package_data=True,
        zip_safe=False,
        install_requires=['Flask', 'Flask-sqlalchemy', 'flask-session',
            'validate_email', 'email', 'decorator'],
        entry_points={
            'paste.app_factory': [ 'main=scratchwire:wsgi_factory' ],
            'paste.app_install': [ 'main=paste.script.appinstall:Installer' ],
            'paste.paster_command': \
                    [ 'load-words=scratchwire.paster:LoadWords' ]
            }
        )
