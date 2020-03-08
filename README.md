# Project 2

Web Programming with Python and JavaScript
https://docs.cs50.net/ocw/web/projects/2/project2.html

**Environment variable**
FLASK_APP=application.py
set SECRET_KEY=AnyString

**Basic Functionality**
Choose username
Create/Join Channel
Chat in real time

**Added Functionality**
Enable Uploading of file and return as a http link for user to download

**Side Note**
The app is designed to use localstorage to track the "lastChannel" and redirect user whenever necessary. This will cause an invalid redirect if the app is restarted while the localstorge is not reset.
