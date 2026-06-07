import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luxe_store.settings')

import django
django.setup()

from django.db import connections
from django.db.migrations.executor import MigrationExecutor

connection = connections['default']
executor = MigrationExecutor(connection)
executor.migrate(executor.loader.graph.leaf_nodes())

from luxe_store.wsgi import application
app = application
