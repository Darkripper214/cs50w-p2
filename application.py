import os

from flask import Flask, session, redirect, render_template, request, jsonify, flash, url_for, send_file, send_from_directory
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room , send
from helper import login_required
from werkzeug.utils import secure_filename
import datetime



app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
UPLOAD_FOLDER = "D:/cODE/CS50 Web/project2/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#Global variable
loggedUser = []
channelCreated = []
channelsMessages= {}


@app.route("/")
@login_required
def index():
    return render_template("index.html", channels=channelCreated)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username=request.form.get("username")
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="Must Provide Username")

        if username in loggedUser:
            return render_template("error.html", message="Username already exists")

        loggedUser.append(username)

        session["username"] = username

        session.permanent = True
        print(loggedUser)
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    # Remove from list
    try:
        loggedUser.remove(session['username'])
    except ValueError:
        pass

    session.clear()

    return redirect("/")

@app.route("/create", methods=["GET","POST"])
def create():
    """ Create a channel and redirect """

    # Get channel name from form
    newChannel = request.form.get("channel")

    if request.method == "POST":

        if newChannel in channelCreated:
            return render_template("error.html", message="channel already exists", channels=channelCreated)

        # Global list tracking list of channel
        channelCreated.append(newChannel)

        # Global dict tracking list of message
        channelsMessages[newChannel] = list()

        return redirect("/channels/" + newChannel)

    else:
        return render_template("create.html", channels=channelCreated)

@app.route("/channels/<channel>", methods=["GET","POST"])
@login_required
def channel(channel):
    """ Send and Receive messages """
    # Updates user current channel
    session["current_channel"] = channel
    if request.method == "POST":
        return redirect("/")
    else:
        try:
            return render_template("channel.html", channels= channelCreated, messages=channelsMessages[channel])
        except KeyError:
            return render_template("error.html", message="channel does not exists", channels= channelCreated)

@socketio.on("joined")
def joined():
    """ to bundle users into SocketIO Room  """

    room = session.get("current_channel")
    join_room(room)
    emit("status", {
        "userJoined": session.get("username"),
        "channel": room,
        "msg": session.get("username") + " has joined the channel"},
        room=room)

@socketio.on("left")
def left():
    """ to de-bundle users into SocketIO Room  """

    room = session.get("current_channel")

    leave_room(room)

    emit("status",
    {"msg": session.get("username") + " has left the channel"},
    room=room)

@socketio.on("sendMessage")
def sendMessage(msg, timestamp):
    """ Collect message     with timestamp """

    room = session.get("current_channel")

    channelsMessages[room].append([timestamp, session.get("username"), msg])

    if len(channelsMessages[room]) > 100:
        # Pop the oldest message
        channelsMessages[room].popleft()

    emit("announceMessage", {
    "user": session.get("username"),
    "timestamp": timestamp,
    "msg": msg},
    room=room)

# Defining allowed file type
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadFile', methods=["POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            fileURL = request.host + url_for('uploads',filename=filename)
            room = session.get("current_channel")
            # Store time of upload
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            channelsMessages[room].append([timestamp, session.get("username"), fileURL])

            if len(channelsMessages[room]) > 100:
                # Pop the oldest message
                channelsMessages[room].popleft()

            # Send link to Channel
            socketio.emit("announceMessage", {
            "user": session.get("username"),
            "timestamp": timestamp,
            "msg": fileURL},
            room=room)
    return redirect("/")

@app.route('/uploads/<filename>', methods=['GET', 'POST'])
def uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
