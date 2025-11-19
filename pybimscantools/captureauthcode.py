"""
Flask app Module to capture authorization code from Catenda Hub
created by thau on 3 OCT 2023. Used as a thread in the program to avoid
program stuck in the flask app running
"""

from flask import Flask, request

from pybimscantools import textcolor


class CaptureAuthCode:
    """ Capture authorization code from Catenda Hub """

    def __init__(self) -> None:
        # Running a Flask app locally to listen to a specific endpoint.
        # When the user gives permission to the application, the server
        # will send a feedback to the specific place which in this case is
        # http://127.0.0.1:5000/callback, which is the place where the flask
        # is listening to. Usually setting place where server responses
        # can be set on the server's application side.
        self.app = Flask(__name__)
        self.authorization_code = None
        self.define_routes()

    def define_routes(self) -> None:
        """ Define routes for the flask app """

        @self.app.route('/callback')
        def callback():
            print(textcolor.colored_text("Callback Executed!", "Green"))
            self.authorization_code = request.args.get('code')
            if self.authorization_code:
                print(textcolor.colored_text(f"Authorization Code ({self.authorization_code}) "
                                             "Received", "Green"))
                # You have successfully obtained the authorization code.
                # Store it securely for the next step.
                return 'Authorization has been completed!\nThe web-browser can now be closed.'
            else:
                return 'Authorization Code not found in the callback URL.'

    def run(self) -> None:
        """ Run the flask app """
        self.app.run()
