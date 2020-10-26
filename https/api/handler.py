# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.1'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import csv
import logging
import psycopg2
import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db')


class PostgreSQL():
    def __init__(self, host='localhost', port=5432, user='umqualquer', password='naomelembro', database='https'):
        self.connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
        self.cursor = self.connection.cursor()

    def municipality_insert(self, name, url):
        try:
            self.cursor.execute('INSERT INTO municipality(name, url) VALUES (%s,%s)', (name, url))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)

    def municipality_select_name(self, name):
        try:
            self.cursor.execute('select url from municipality where name=%s', (name,))
            municipality_url = self.cursor.fetchone()[0]
            return municipality_url
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)
            return None

    def municipality_select_all(self):
        try:
            self.cursor.execute('select name from municipality')
            records = self.cursor.fetchall()
            rv = []
            for row in records:
                rv.append(row[0])
            return rv
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)
            return []

    def qualities_insert(self, url, date, https, certificate, redirect, r301, hsts):
        try:
            self.cursor.execute('select id from municipality where url=%s', (url,))
            municipality_id = self.cursor.fetchone()[0]
            self.cursor.execute('INSERT INTO qualities(date, id, https, certificate, redirect, r301, hsts) VALUES (%s, %s, %s, %s, %s, %s, %s)', (date, municipality_id, https, certificate, redirect, r301, hsts))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)

    def defects_insert(self, url, date, redirect, r301, similarity):
        try:
            self.cursor.execute('select id from municipality where url=%s', (url,))
            municipality_id = self.cursor.fetchone()[0]
            self.cursor.execute('INSERT INTO defects(date, id, redirect, r301, similarity) VALUES (%s, %s, %s, %s, %s)', (date, municipality_id, redirect, r301, similarity))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)

    def select_test_municipality(self, name):
        try:
            self.cursor.execute('select id from municipality where name=%s', (name,))
            municipality_id = self.cursor.fetchone()[0]

            self.cursor.execute('select qualities.date, https, certificate, qualities.redirect, qualities.r301, hsts, defects.redirect, defects.r301, similarity from qualities inner join defects ON qualities.id = defects.id AND qualities.date = defects.date where qualities.id=%s', (municipality_id,))
            rv = []
            records = self.cursor.fetchall()
            for row in records:
                rv.append({'date':row[0],'https':row[1],'certificate':row[2],'http_redirect': row[3],'http_r301':row[4],'hsts':row[5], 'https_redirect':row[6],'https_r301':row[7],'similarity':row[8]})
            return rv
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)
            return {}

    def tests_select(self):
        try:
            self.cursor.execute('select distinct date from qualities')
            records = self.cursor.fetchall()
            rv = []
            for row in records:
                rv.append(row[0])
            return rv
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)
    
    def select_test(self, date):
        try:
            self.cursor.execute('select municipality.name, qualities.date, https, certificate, qualities.redirect, qualities.r301, hsts, defects.redirect, defects.r301, similarity from municipality inner join qualities on qualities.id = municipality.id inner join defects ON qualities.id = defects.id AND qualities.date = defects.date where qualities.date=%s', (date,))
            rv = []
            records = self.cursor.fetchall()
            for row in records:
                rv.append({'municipality':row[0], 'date':row[1],'https':row[2],'certificate':row[3],'http_redirect': row[4],'http_r301':row[5],'hsts':row[6], 'https_redirect':row[7],'https_r301':row[8],'similarity':row[9]})
            return rv
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)

    def test_select(self, name, date):
        try:
            self.cursor.execute('select id from municipality where name=%s', (name,))
            municipality_id = self.cursor.fetchone()[0]

            self.cursor.execute('select https,certificate,redirect,r301,hsts from qualities where id=%s and date=%s', (municipality_id, date))
            record = self.cursor.fetchone()
            rv = {'date':date,
            'https':record[0],
            'certificate':record[1],
            'http_redirect': record[2],
            'http_r301':record[3],
            'hsts':record[4]}

            self.cursor.execute('select redirect,r301,similarity from defects where id=%s and date=%s', (municipality_id, date))
            record = self.cursor.fetchone()
            rv['https_redirect']=record[0]
            rv['https_r301']=record[1]
            rv['similarity']=record[2]

            return rv
        except Exception as e:
            self.connection.rollback()
            logger.exception(e)
            return {}

    def close(self):
        self.cursor.close()
        self.connection.close()
