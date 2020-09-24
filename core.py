from flask import Flask, render_template, request, redirect
import iterator60
import pickle
import os
import sqlite3

app = Flask(__name__, template_folder='templates')


hostName = '192.168.1.30'
last = '1'


def save():
    global last
    with open('iter.pkl', 'wb') as f:
        pickle.dump(last, f)


def prepareSql():
    with sqlite3.connect('linksData.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS links
                       (shortlink TEXT NOT NULL PRIMARY KEY, link TEXT NOT NULL)
                       WITHOUT ROWID""")
        connect.commit()


def generateNewLink(link):
    global last
    if not ('http://' in link or 'https://' in link):
        link = 'http://' + link
    link_out = hostName + '/' + last
    last = iterator60.goNext(last)
    save()
    updateData(link, link_out)
    return link_out


def updateData(link, shortLink):
    with sqlite3.connect('linksData.db') as connect:
        cursor = connect.cursor()
        data = (shortLink, link)
        cursor.execute("""INSERT INTO links VALUES (?, ?)""", data)
        connect.commit()


def getLink(shortLink):
    with sqlite3.connect('linksData.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""SELECT * FROM links WHERE shortlink=?""", (shortLink,))
        links = cursor.fetchone()
        if links is not None:
            link = links[1]
        else:
            link = 'unsupported.link'
        return link


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        link = request.form.get('link_in')
        link_out = generateNewLink(link)
        return render_template('index.html', link_out=link_out)


@app.route('/<link>', methods=['GET'])
def chLink(link):
    if link == 'favicon.ico' or link == 'unsupported.link':
        return render_template('index.html')
    return redirect(getLink(hostName + '/' + link))


if __name__ == '__main__':
    prepareSql()
    if os.path.exists('iter.pkl'):
        with open('iter.pkl', 'rb') as file:
            last = pickle.load(file)
    else:
        save()
    app.run(host=hostName, port='80', debug=False)
