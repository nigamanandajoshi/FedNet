"""Flask API application."""

from flask import Flask, jsonify
from flask_cors import CORS
from config.settings import settings
from config.logging_config import setup_logging
from .routes import api_bp

# Setup logging
logger = setup_logging(log_level=settings.log_level, log_dir=settings.logs_dir)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.secret_key
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max request size

# Enable CORS
CORS(app)

# Rate limiting
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per minute", "5000 per hour"],
        storage_uri="memory://",
    )
    logger.info("Rate limiting enabled: 200/min, 5000/hr")
except ImportError:
    limiter = None
    logger.warning("flask-limiter not installed — rate limiting disabled")

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'fednet-api',
        'version': '1.0.0'
    })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(429)
def ratelimit_handler(error):
    """Handle rate limit exceeded."""
    return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429


def main():
    """Run the API server."""
    logger.info(f"Starting FedNet API server on {settings.api_host}:{settings.api_port}")
    app.run(
        host=settings.api_host,
        port=settings.api_port,
        debug=settings.api_debug
    )


if __name__ == '__main__':
    main()
