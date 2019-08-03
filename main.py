from flask import Flask, request, render_template, redirect, jsonify
from urllib.parse import urlparse
import sqlite3, base64
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import hashlib
import random

app = Flask(__name__)


limiter = Limiter(app, key_func=get_remote_address)
host = 'http://localhost:5000/'

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("1 per second")
def index():
	if request.method == 'POST':
		url = str.encode(request.form.get('url'))
		hashObject = hashlib.md5(url)
		shortUrl = hashObject.hexdigest()[:7]
		urlalias = url.decode('utf-8')
		shortened = []
		with sqlite3.connect('urls.db') as conn:
			cursor = conn.cursor()
			shortened = cursor.execute(
					'SELECT SHORTURL FROM URL WHERE URL=?',[base64.urlsafe_b64encode(url)]).fetchall()
			print(shortened)
		while (base64.urlsafe_b64encode(str.encode(shortUrl)),) in shortened:
			urlalias += str(random.randint(0, 9))
			hashObject = hashlib.md5(str.encode(urlalias))
			shortUrl = hashObject.hexdigest()[:7]

		if urlparse(url).scheme == '':
			url = 'http://' + url
		
		with sqlite3.connect('urls.db') as conn:
			cursor = conn.cursor()
			res = cursor.execute(
				'INSERT INTO URL (URL, SHORTURL) VALUES (?,?)',
				[base64.urlsafe_b64encode(url), base64.urlsafe_b64encode(str.encode(shortUrl))]
			)
		return render_template('home.html', short_url=host + shortUrl)
	return render_template('home.html')

@app.route('/<short_url>')
def redirect_url(short_url):
	url = host
	with sqlite3.connect('urls.db') as conn:
		cursor = conn.cursor()
		res = cursor.execute('SELECT URL FROM URL WHERE SHORTURL=?',[base64.urlsafe_b64encode(str.encode(short_url))])
		try:
			short = res.fetchone()
			if short is not None:
				url = base64.urlsafe_b64decode(short[0])
		except Exception as e:
			print(e)
	return redirect(url)

@app.route('/stats')
def stats():
	res = []
	with sqlite3.connect('urls.db') as conn:
		cursor = conn.cursor()
		res = cursor.execute('SELECT * FROM URL').fetchall()
	entries = []
	for id, longUrl, shortUrl in res:
		data = {'long_url': base64.urlsafe_b64decode(longUrl).decode('utf-8'), 'short_url': base64.urlsafe_b64decode(shortUrl).decode('utf-8')}
		entries.append(data)
	return jsonify(entries)
	

if __name__ == '__main__':
	#create_table()
	app.run(debug=True)
