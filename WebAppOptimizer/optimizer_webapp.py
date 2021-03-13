from WebAppOptimizer.app import create_app, db
from WebAppOptimizer.app.models import User, Configuration

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Configuration': Configuration}
