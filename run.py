import os
from novastore import create_app

app = create_app()

if __name__ == '__main__':
    # Désactiver le debug en production
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='127.0.0.1')

