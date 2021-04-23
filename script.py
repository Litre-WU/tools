from mitmproxy import http, ctx, proxy
import pymongo
from datetime import datetime


class Joker:
    def __init__(self):
        self.ip = ""
        self.pymongo_client = ""
        self.db = self.pymongo_client["data"]

    def clientconnect(self, layer: proxy.protocol.Layer):
        self.ip = layer.client_conn.address[0]

    def save_data(self, *args):
        mycol = args[0]
        data_list = args[1]
        data_list = [{**d, **{"collect_time": datetime.now()}} for d in data_list]
        try:
            return mycol.insert_many(data_list).inserted_ids
        except Exception as e:
            # print(e)
            for x in data_list:
                try:
                    mycol.insert_one(x)
                except Exception as e:
                    # print(e)
                    mycol.find_one_and_update({"_id": x["_id"]}, {"$set": x})
        self.pymongo_client.close()

    def request(self, flow: http.HTTPFlow) -> None:
        pass
        # ip = '.'.join(str(randint(0, 255)) for _ in range(4))
        # flow.request.headers.update({
        #     # "User-Agent": generate_user_agent(),
        #     # "X-Forwarded-For": ip,
        #     # "X-Real-IP": ip,
        # })

    def response(self, flow: http.HTTPFlow) -> None:
        pass
        # if 'http://rcpu.cwun.org/UnInfo.aspx' == flow.request.url:
        #     print("*" * 10)
        #     text = flow.response.text


addons = [Joker()]

if __name__ == '__main__':
    mydb = myclient["data"]
    mycol = mydb["test"]
    rs = mycol.find_one({"_id": "319fa651-4b2d-4f44-b432-a9b527dd7d2f"})
    print(rs)
