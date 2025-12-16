"""
Main Flask application for TMHNA Financial AI Assistant.

This module initializes the Flask app, configures extensions,
and registers all blueprints for routing.
"""
# Converted from Campus Resource Hub to TMHNA Financial AI Assistant

from flask import Flask, render_template
import os
from datetime import datetime

# Import TMHNA blueprints
from src.controllers.financial_analysis import financial_bp
from src.controllers.master_data_matching import master_data_bp


def create_app():
    """
    Application factory function.
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__,
                template_folder='views',
                static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@campushub.edu')
    app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND', 'true').lower() == 'true'  # Suppress in dev
    
    # Register TMHNA blueprints
    app.register_blueprint(financial_bp)
    app.register_blueprint(master_data_bp)
    
    # Context processors - make variables available to all templates
    @app.context_processor
    def inject_globals():
        """Inject global variables into all templates."""
        return {
            'current_year': datetime.now().year,
            'app_name': 'TMHNA Financial AI Assistant'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    # Home route - SharePoint-styled landing page
    @app.route('/')
    def index():
        """SharePoint-styled homepage for TMHNA Financial AI Assistant."""
        return render_template('sharepoint_home.html')
    
    # Original landing page route
    @app.route('/original')
    def original_home():
        """Original homepage for TMHNA Financial AI Assistant."""
        return render_template('tmhna_home.html')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'app': 'TMHNA Financial AI Assistant'}, 200
    
    return app


if __name__ == '__main__':
    # Initialize financial database if it doesn't exist
    from src.models.financial_db import DATABASE_PATH, init_financial_database, seed_financial_data
    import os
    
    if not os.path.exists(DATABASE_PATH):
        print("Financial database not found. Initializing...")
        init_financial_database()
        seed_financial_data()
    
    # Create and run app
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

