from paste.script.command import Command, BadCommand
from paste.deploy import loadapp
from scratchwire.model import db, Noun, Adjective
import os
import re

class LoadWords(Command):
    summary = "Load the scratchwire noun and adjective lists"
    usage = "CONFIG_FILE [var=value]"
    group_name = "scratchwire"
    parser = Command.standard_parser(verbose = False)

    parser.add_option('-n', '--nouns', action='store', type='string', \
            dest='nounfile', help="file to load nouns from")

    parser.add_option('-a', '--adjs', action='store', type='string', \
            dest='adjfile', help="file to load adjectives from")
    parser.add_option('--app-name', action='store', type='string', \
            dest='appname', default='main', help="App name to load")

    _scheme_re = re.compile(r'^[a-z][a-z]+:', re.I)

    def command(self):
        if not self.args or len(self.args) == 0:
            raise BadCommand("You must specify a config")

        app_spec = self.args.pop(0)

        if not self._scheme_re.search(app_spec):
            app_spec = 'config:' + app_spec

        app = loadapp(app_spec, name=self.options.appname, \
                relative_to=os.getcwd(), **self.parse_vars(self.args))

        if self.options.adjfile:
            self.load_words(self.options.adjfile, Adjective)
        if self.options.nounfile:
            self.load_words(self.options.nounfile, Noun)

    @staticmethod
    def load_words(data_file, model):
        with open(data_file, 'r') as data:
            for line in data:
                db.session.add(model(line.strip()))
        db.session.commit()
