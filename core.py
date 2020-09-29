from flask import Flask, render_template, request, redirect
import iterator60
import pickle
import os
import sqlite3
import cfg
import s_logger as log

app = Flask(__name__, template_folder='templates')

hostName = cfg.hostName  # YOUR HOSTNAME
log.noPrint = True
last = '1'  # DONT TOUCH


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
        cursor.execute("""CREATE TABLE IF NOT EXISTS pwds
                       (shortlink TEXT NOT NULL PRIMARY KEY, pwd TEXT NOT NULL)
                       WITHOUT ROWID""")
        connect.commit()
        log.log('SQL Prepared stage done')


def generateNewLink(link):
    global last
    last = iterator60.goNext(last)
    if not ('http://' in link or 'https://' in link):
        link = 'http://' + link
    link_out = hostName + '/' + last
    if last in link and hostName in link:
        link_out = hostName
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


def setPwd(shortLink, pwd):
    if pwd == '':
        return
    with sqlite3.connect('linksData.db') as connect:
        cursor = connect.cursor()
        data = (shortLink, pwd)
        cursor.execute("""INSERT INTO pwds VALUES (?, ?)""", data)
        connect.commit()


def checkPwd(link):
    with sqlite3.connect('linksData.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""SELECT EXISTS(SELECT 1 FROM pwds WHERE shortlink=?);""", (link,))
        data = cursor.fetchone()
        hasPwd = data[0]
    if hasPwd:
        return True
    else:
        return False


def validatePwd(link, pwd):
    with sqlite3.connect('linksData.db') as connect:
        cursor = connect.cursor()
        cursor.execute("""SELECT * FROM pwds WHERE shortlink=?""", (link,))
        data = cursor.fetchone()
    if pwd == data[1]:
        return True
    else:
        return False


@app.after_request
def log_the_status_code(response):
    if type(response) is not None:
        status = response.status
        log.log(str(status) + '\n')
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    log.log(str(request.method) + ' /' + '\n')
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        userType = request.form.get('userType')
        link = request.form.get('link_in')
        if link == '':
            return render_template('index.html')
        link_out = generateNewLink(link)
        log.log(str(userType) + ' created new link\n' + str(link) + '\n' + str(link_out) + '\n')
        if request.form.get('set_pwd'):
            pwd = request.form.get('pwd_in')
            setPwd(link_out, pwd)
        if userType not in ('telegramBot', 'vkBot'):
            return render_template('index.html', link_out=link_out)
        else:
            return link_out


@app.route('/<link>', methods=['GET'], strict_slashes=False)
def chLink(link):
    log.log(str(request.method) + ' /' + link + '\n')
    if link == 'favicon.ico' or link == 'unsupported.link':
        return redirect('http://' + hostName)
    link = hostName + '/' + link
    if checkPwd(link):
        return render_template('redirector.html')
    else:
        return redirect(getLink(link))


@app.route('/<link>/<pwd>', methods=['GET'], strict_slashes=False)
def verifyPwd(link, pwd):
    log.log(str(request.method) + ' /' + link + '/' + pwd + '\n')
    link = hostName + '/' + link
    if checkPwd(link):
        if validatePwd(link, pwd):
            return redirect(getLink(link))
        else:
            return redirect('http://' + hostName)
    else:
        return 'hello'


@app.route('/<a>/<b>/<c>', methods=['GET'], strict_slashes=False)
def terminator():
    return redirect('http://' + hostName)


if __name__ == '__main__':
    prepareSql()
    if os.path.exists('iter.pkl'):
        with open('iter.pkl', 'rb') as file:
            last = pickle.load(file)
    else:
        save()
    log.log('\n' + 28 * '_' + '\nStarting the core of linkcut\n' + 28 * '_' + '\n')
    app.run(host=hostName, port='80', debug=False)
