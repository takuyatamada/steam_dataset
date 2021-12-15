import json
import sqlite3
import requests
import re
def main():
    # path = "steam_new.json"
    # path = "steam_games.json"
    path = 'australian_user_reviews.json'
    # path = 'australian_users_items.json'


    
    count=0
    with open(path, encoding="utf-8") as f:
        for line in f:
            count+=1
            # if count==200:
            #     break

            #一度シングルクォーテーションをすべてダブルクォーテーションに変更
            line_rep = line.replace("'","\"")
            #各reviewのrecommend:においてTrue,Falseの値がクォーテーションで囲まれていないので明示的に囲む
            line_rep = line_rep.replace("True","\"True\"")
            line_rep = line_rep.replace("False","\"False\"")


            #以下のtryではじかれるのはreviewsが空、そのユーザがなにもレビューしていない場合
            try:
                reviews = re.search(r'\"review\": .*?}',line_rep).group()
                # reviews = re.findall(r'\"review\": .*?}',line_rep)
            except:
                # print('ダメでした')
                # print(line_rep)
                continue        


            #各ユーザに紐づいているレビューをひと一つずつ分割する、こうすることでレビュー本文のダブルクォーテーションをシングルクォーテーションに変更する作業ができる
            try:
                # reviews = re.search(r'\"review\": .*?}',line_rep).group()
                reviews = re.findall(r'\"review\": .*?}',line_rep)
            except:
                # print('ダメでした')
                # print(line_rep)
                continue
            # print(reviews)

            replace_json = line_rep
            for review in reviews:
            #     print("----")
                #レビュー本文をとってくる
                review_content = review[11:-2]
                # print(review_content)
                review_content_delete_doublq = review_content.replace("\"","\'")
                # print(review_content_delete_doublq)
                #本文と前後のjsonテキストをくっつける
                insert_review_json = review[:11]+review_content_delete_doublq+review[-2:]
                #\が入っていてエラーになることが多いからそこの処理
                insert_review_json = insert_review_json.replace('\\','')
                # print(insert_review_json)
                #元のjsonテキストと置き換える
                replace_json = replace_json.replace(review,insert_review_json)
                
            # print(replace_json)

            #上の処理でどうしても無理なものはごめんなさいする(10件くらい)
            try:
                line_json = json.loads(replace_json)
            except:
                print('json loads エラー')
                # print(replace_json)
                continue
            # print(line_json)
            # print(line_json['reviews'][0]['review'])
            # print(line)
            dump_dp(line_json)
            if line_json['user_id']=="154352":
                print(line)

    print(count)

def dump_dp(line_json):
    con = sqlite3.connect('steam.db')
    cur = con.cursor()
    from fasttext import load_model


    # for one_line in line_json:
    #     print('one_line',one_line)
    #     user_id = one_line['user_id']
    user_id = line_json['user_id']
    for one_review in line_json['reviews']:
        item_id = one_review['item_id']
        review_text = one_review['review']
        if one_review['recommend']=='True':
            rating = 1
        elif one_review['recommend']=='False':
            rating = 0
        _tmp = [user_id,item_id,rating,review_text]
        # print(_tmp)
        cur.execute('insert or ignore into review (user_id,item_id,rating,review) values(?,?,?,?)',_tmp)
        # パスを書き換えてください
        model = load_model("../bin/lid.176.bin")
        model.predict("Arcadian Landscape with Shepherds and Cattle")
        # if user_id = '154352':
        #     print(line_json)
    con.commit()

def translate(text):
    url = "https://script.google.com/macros/s/AKfycbzZtvOvf14TaMdRIYzocRcf3mktzGgXvlFvyczo/exec?text="+ text + "&source=&target=en"
    response = requests.get(url)
    jsonData = response.json()
    print(jsonData["text"])
    return jsonData["text"]

if __name__ == '__main__':
    # main()
    # translate("O jogo que vc pode fazer quase tudo e tem ate fase e parkour esse jogo é muito bom")