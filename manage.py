# coding=utf-8
import os
import coverage
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, prompt_bool

from app import create_app, db

COV = None
if os.environ.get('FLASK_COVERAGE'):
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)  # initializes manager and registers the app
migrate = Migrate(app, db)  # initializes migration and registers the app


def make_shell_context():
    # creates a dictionary of all the objects that can be accessed in shell
    return dict(app=app, db=db)

manager.add_command('shell',
                    Shell(banner="Welcome to Url-Shortener Python shell"),
                    make_context=make_shell_context())
manager.add_command('db', MigrateCommand)


@manager.command
def dropdb():
    if prompt_bool("Are you sure you want to loose all your data"):
        db.drop_all()
        print("Dropped the database")


@manager.command
def test():
    """Runs the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == "__main__":
    try:
        manager.run()
    except SystemError:
        print("An unexpected error occurred")
