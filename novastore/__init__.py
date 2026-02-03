from flask import Flask


def create_app(config_object=None):
    """Factory to create and configure the Flask app."""
    # Templates live in ../templates, static in ../static for now
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Configuration
    if config_object is None:
        from .config import DevConfig
        app.config.from_object(DevConfig)
    else:
        app.config.from_object(config_object)

    # Register blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.api_panier import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
