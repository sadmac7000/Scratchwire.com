from setuptools import setup
setup(
        name='ScratchWire.com',
        version='0.1',
        long_description=__doc__,
        packages=['scratchwire'],
        include_package_data=True,
        zip_safe=False,
        install_requires=['Flask', 'Flask-sqlalchemy', 'flask-session',
            'validate_email'],
        entry_points={
            'paste.app_factory': [ 'main=scratchwire:wsgi_factory' ],
            'paste.app_install': [ 'main=paste.script.appinstall:Installer' ]
            }
        )
