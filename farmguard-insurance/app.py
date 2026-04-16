from flask import Flask, render_template
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    from api.weather_routes import weather_bp
    from api.blockchain_routes import blockchain_bp

    app.register_blueprint(weather_bp, url_prefix='/api/weather')
    app.register_blueprint(blockchain_bp, url_prefix='/api/blockchain')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)