from flask import Flask, request, render_template, redirect
from db import create_table
from urllib.parse import urlparse
import sqlite3, base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib

app = Flask(__name__)


limiter = Limiter(app, key_func=get_remote_address)
host = 'http://localhost:5000/'

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("1 per second")
def index():
	if request.method == 'POST':
		url = str.encode(request.form.get('url'))
		hashObject = hashlib.md5(url)
		shortUrl = hashObject.hexdigest()[:8]

		if urlparse(url).scheme == '':
			url = 'http://' + url
		
		with sqlite3.connect('urls.db') as conn:
			cursor = conn.cursor()
			res = cursor.execute(
				'INSERT INTO URL (URL, SHORTURL) VALUES (?,?)',
				[base64.urlsafe_b64encode(url), shortUrl]
			)
		return render_template('home.html', short_url=host + shortUrl)
	return render_template('home.html')

@app.route('/<short_url>')
def redirect_url(short_url):
	url = host
	with sqlite3.connect('urls.db') as conn:
		cursor = conn.cursor()
		res = cursor.execute('SELECT URL FROM URL WHERE SHORTURL=?',[short_url])
		try:
			short = res.fetchone()
			if short is not None:
				print(short[0][0])
				url = base64.urlsafe_b64decode(short[0])
		except Exception as e:
			print(e)
	return redirect(url)

if __name__ == '__main__':
	create_table()
	app.run(debug=True)
