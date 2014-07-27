import os

import flask
from flask import request, render_template, redirect, flash
import praw


app = flask.Flask(__name__)
app.secret_key = os.urandom(30)

reddit = praw.Reddit('hearddit bot')


# home page
@app.route('/', methods=['get', 'post'])
def home():
    if request.method == 'POST':
        subreddit = request.form['subreddit']
        category = request.form.get('category', None)
        if category is None:
            return redirect('/play/%s' % subreddit)
        return redirect('/play/%s/%s' % (subreddit, category))
    return render_template('index.html')


# listen to a subreddit
@app.route('/play/<subreddit>', methods=['get'])
@app.route('/play/<subreddit>/<category>', methods=['get'])
def listen(subreddit, category='hot'):

    subr = reddit.get_subreddit(subreddit)

    if category is None:
        category = 'hot'

    if category == 'hot':
        submissions = [s for s in subr.get_hot(limit=50)]
    elif category == 'new':
        submissions = [s for s in subr.get_new(limit=50)]
    elif category == 'controversial':
        submissions = [s for s in subr.get_controversial(limit=50)]
    else:
        submissions = []
        flash("Sorry, I couldn't find anything at r/%s/%s" % (subreddit, category))

    videos = [
        s.media['oembed']
        for s in submissions
        if s.media and s.media['oembed']['provider_name'].lower() == 'youtube'
    ]

    playlist = [
        v['url'].split('v=')[-1] for v in videos
    ]
    playlist = "['%s']" % "','".join(playlist)
    try:
        first = "'%s'" % videos[0]['url'].split('v=')[-1]
    except IndexError:
        first = ''

    return render_template('play.html', first=first, playlist=playlist)


# main loop
if __name__ == '__main__':
    app.run(debug=True)
