#! /usr/bin/env python
# -*- coding: utf-8 -*-

import flask
from mybot import r, ALL_KEYWORDS

app = flask.Flask(__name__)


@app.route('/')
def index():
    return '<body> %s </body>' % '<br/>'.join(r.smembers(ALL_KEYWORDS))


if __name__ == '__main__':
    import sys
    args = sys.argv
    app.run(host="0.0.0.0", port=args[1])
