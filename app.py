import logging
import posix_ipc
import re
from functools import wraps
from flask import Flask, render_template, flash, redirect, request, Response

from system import System


app = Flask(__name__)
app.config.from_pyfile("app.cfg")
try:
    mq = posix_ipc.MessageQueue("/epdtext_ipc")
    mq.block = False
except posix_ipc.PermissionsError:
    logging.error("couldn't open message queue")
    exit(1)


# Authentication decorator
def check_auth(username, password):
    """Check if username/password combination is valid."""
    return (username == app.config.get('AUTH_USERNAME', 'admin') and
            password == app.config.get('AUTH_PASSWORD', 'changeme'))


def authenticate():
    """Sends a 401 response that enables basic auth."""
    return Response(
        'Authentication required. Please login to access epdtext-web.',
        401,
        {'WWW-Authenticate': 'Basic realm="epdtext-web"'}
    )


def requires_auth(f):
    """Decorator to require HTTP Basic Auth on routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


# Input validation
def validate_screen_name(screen_name):
    """
    Validate screen name to prevent command injection.
    Only allow alphanumeric characters, underscores, hyphens, and dots.
    """
    if not screen_name:
        return None
    # Allow only safe characters: letters, numbers, underscore, hyphen, dot
    if not re.match(r'^[a-zA-Z0-9_.-]+$', screen_name):
        return None
    # Limit length
    if len(screen_name) > 100:
        return None
    return screen_name


@app.route('/')
@requires_auth
def index():
    return render_template('index.html', system=System)


@app.route('/next_screen')
@requires_auth
def next_screen():
    mq.send("next", timeout=10)
    flash("Sent 'next' message to epdtext")
    return redirect('/')


@app.route('/previous_screen')
@requires_auth
def previous_screen():
    mq.send("previous", timeout=10)
    flash("Sent 'previous' message to epdtext")
    return redirect('/')


@app.route('/button0')
@requires_auth
def button0():
    mq.send("button0", timeout=10)
    flash("Sent 'KEY1' message to epdtext")
    return redirect('/')


@app.route('/button1')
@requires_auth
def button1():
    mq.send("button1", timeout=10)
    flash("Sent 'KEY2' message to epdtext")
    return redirect('/')


@app.route('/button2')
@requires_auth
def button2():
    mq.send("button2", timeout=10)
    flash("Sent 'KEY3' message to epdtext")
    return redirect('/')


@app.route('/button3')
@requires_auth
def button3():
    mq.send("button3", timeout=10)
    flash("Sent 'KEY4' message to epdtext")
    return redirect('/')


@app.route('/reload')
@requires_auth
def reload():
    mq.send("reload", timeout=10)
    flash("Sent 'reload' message to epdtext")
    return redirect('/')


@app.route('/screen')
@requires_auth
def screen():
    screen_name = request.args.get('screen')
    screen_name = validate_screen_name(screen_name)
    if not screen_name:
        flash("Invalid screen name. Only alphanumeric, underscore, hyphen, and dot allowed.", "error")
        return redirect('/')
    mq.send("screen " + screen_name, timeout=10)
    flash("Sent 'screen' message to epdtext")
    return redirect('/')


@app.route('/add_screen')
@requires_auth
def add_screen():
    screen_name = request.args.get('screen')
    screen_name = validate_screen_name(screen_name)
    if not screen_name:
        flash("Invalid screen name. Only alphanumeric, underscore, hyphen, and dot allowed.", "error")
        return redirect('/')
    mq.send("add_screen " + screen_name, timeout=10)
    flash("Sent 'add_screen' message to epdtext")
    return redirect('/')


@app.route('/remove_screen')
@requires_auth
def remove_screen():
    screen_name = request.args.get('screen')
    screen_name = validate_screen_name(screen_name)
    if not screen_name:
        flash("Invalid screen name. Only alphanumeric, underscore, hyphen, and dot allowed.", "error")
        return redirect('/')
    mq.send("remove_screen " + screen_name, timeout=10)
    flash("Sent 'remove_screen' message to epdtext")
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
