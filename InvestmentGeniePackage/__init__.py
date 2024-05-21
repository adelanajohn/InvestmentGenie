from flask import Flask

from InvestmentGeniePackage import (
    errors,
    pages
)

def create_app():
    app = Flask(__name__)
    app.secret_key = 'w4&L#3$Qc5@g'

    app.register_blueprint(pages.bp)
    app.register_error_handler(404, errors.page_not_found)
    return app