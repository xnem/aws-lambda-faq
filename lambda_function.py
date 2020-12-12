import psycopg2
import json
import urllib.parse


class Database():

    class Parameter():

        def __init__(self, host, port, dbname, user, password):
            self.host = host
            self.port = port
            self.dbname = dbname
            self.user = user
            self.password = password

    def __init__(self, param):
        self.db = param
        self.header = tuple()
        self.records = list()
        self.counts = int()

    def _connection(self):

        print('connect to db: {}/{}'.format(self.db.host, self.db.dbname))
        return psycopg2.connect(
            host=self.db.host,
            port=self.db.port,
            dbname=self.db.dbname,
            user=self.db.user,
            password=self.db.password
        )

    def search_qanda(self, word):
        try:
            with self._connection() as conn:
                with conn.cursor() as cursor:
                    sql = "SELECT id, question, answer FROM faq_qanda WHERE id IN (SELECT qandaid FROM faq_index WHERE token = \'" + word + "\' ORDER BY count);"
                    cursor.execute(sql)
                    searched_list = cursor.fetchall()
                return searched_list
        except Exception:
            print("search_qandaに失敗")
            import traceback
            traceback.print_exc()
            if sql is not None:
                print("SQL:" + sql)
            raise Exception
    
    
    def search_qanda2(self, splited_words):
        try:
            searched_lists = []
            with self._connection() as conn:
                with conn.cursor() as cursor:
                    for word in splited_words:
                        sql = "SELECT id, question, answer FROM faq_qanda WHERE id IN (SELECT qandaid FROM faq_index WHERE token = \'" + word + "\' ORDER BY count);"
                        cursor.execute(sql)
                        searched_lists = cursor.fetchall()
                        searched_lists += searched_lists
                    searched_lists = sorted([x for x in set(searched_lists) if searched_lists.count(x) > 1], key=searched_lists.index)  # 重複している項目のみ取り出す
                return searched_lists
        except Exception:
            print("search_qanda2に失敗")
            if sql is not None:
                print("SQL:" + sql)
            raise Exception


def lambda_handler(event, context):
    print('event: {}'.format(event))
    print('context: {}'.format(context))
    word = event['body'].split("&")[8].split("=")[1]
    word = urllib.parse.unquote(word)

    param = Database.Parameter(
        host='',
        port='',
        dbname='u0000faq',
        user='postgres',
        password='postgres'
    )

    db = Database(param=param)
    try:
        splited_words = word.split()
        if len(splited_words) == 1:  # 検索ワードが１つ
            searched_list = db.search_qanda(splited_words[0])
        else:  # 検索ワードがスペース挟んで複数
            searched_list = db.search_qanda2(splited_words)
        
        body = searched_list[0][1] + " " + searched_list[0][2]
        response = {
            "statusCode": 200,
            "headers": {
                'Content-Type': 'application/json'
            },
            "body": json.dumps(body, ensure_ascii=False),
            "isBase64Encoded": 'false'
        }
        print(response)
        return response
    except Exception:
        return {
            'status_code': 500
        }


if __name__ == '__main__':
    print(lambda_handler(event=None, context=None))