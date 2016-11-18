#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 WooParadog <guohaochuan@gmail.com>
#
# Distributed under terms of the MIT license.

import flask
from mybot import r, ALL_KEYWORDS

app = flask.Flask(__name__)


@app.route('/')
def index():
    return '<body> %s </body>' % '<br/>'.join(r.smembers(ALL_KEYWORDS))


if __name__ == '__main__':
    import sys
    args = sys.argv
    app.run(port=args[1])
