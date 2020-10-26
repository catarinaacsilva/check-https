# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import io
import csv
import json
from handler import PostgreSQL
from flask import Flask, jsonify, request, Response


app = Flask(__name__)


@app.route('/api/', methods=['GET'])
def get_info():
    d = {'Author': __author__,
    'EMail':__email__,
    'Version':__version__}
    return jsonify(d)


@app.route('/api/municipality', methods=['GET'])
def get_municipality():
    db = PostgreSQL()
    rv = db.municipality_select_all()
    db.close()
    d = {'municipality':rv}
    return jsonify(d)


@app.route('/api/tests', methods=['GET'])
def get_test():
    name = request.args['name']
    db = PostgreSQL()
    rv = db.select_test_municipality(name)
    db.close()
    d = {'tests':rv}
    return jsonify(d)


@app.route('/api/dates', methods=['GET'])
def get_dates():
    db = PostgreSQL()
    rv = db.tests_select()
    db.close()
    d = {'dates':rv}
    return jsonify(d)

@app.route('/api/export', methods=['GET'])
def get_export():
    date = request.args['date']
    db = PostgreSQL()
    rv = db.select_test(date)
    db.close()
    keys = rv[0].keys()
    f = io.StringIO()
    dict_writer = csv.DictWriter(f, keys)
    dict_writer.writeheader()
    dict_writer.writerows(rv)
    return Response(f.getvalue(), mimetype='text/csv', headers={"Content-disposition":
    'attachment; filename=export.csv'})


if __name__ == "__main__":
    app.run(host='0.0.0.0')
