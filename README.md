# Scratchwire.com #

Scratchwire.com is a web application for discretely sharing STD results with
partners.

## Installation ##
You can install the Scratchwire.com app with
[setuptools](https://bitbucket.org/pypa/setuptools):

~~~
$ python setup.py install
~~~

The application is deployed with [paste](http://pythonpaste.org/). The
`develop.ini.example` file contains sample configuration suitable for
development. You can use `paster setup-app <config file>` to initialize the
database.

Scratchwire assigns random aliases to its users so they can interact
anonymously. This functionality depends on a list of nouns and a list of
adjectives in the database. These tables can be populated with the paster
command `paster load-words`. Run with `--help` for details.
