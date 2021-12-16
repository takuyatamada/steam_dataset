import json
import sqlite3
import requests
import re
import time
from googletrans import Translator
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
    # from fasttext import load_model


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
        # model = load_model("../bin/lid.176.bin")
        # model.predict("Arcadian Landscape with Shepherds and Cattle")
        # if user_id = '154352':
        #     print(line_json)
    con.commit()

def translate_main(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('select user_id,item_id,rating,review from review where review != "" and translate_review is null ')
    columns = cur.fetchall()
    # print(columns)
    count = 0
    for column in columns:
        count+=1
        if count==1:
            continue
        if column[0]=='inf':
            continue
        print(column)
        
        translate_text = translate(column[3])
        # print('column3',column[3])
        # translate_text = googletrans(column[3])
        time.sleep(1)
        # print(translate_text)
    
        #DBに挿入
        sql = 'update review set translate_review= "'+translate_text+'" where user_id= "'+str(column[0])+'" and item_id= '+str(column[1])
        print(sql)
        cur.execute(sql)
        con.commit()
        #dbここまで

        # except:
        #     continue  

def translate(text):
    url = "https://script.google.com/macros/s/AKfycbzZtvOvf14TaMdRIYzocRcf3mktzGgXvlFvyczo/exec?text="+ text + "&source=&target=en"
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    # text = text.decode('utf-8')
    # try:
    #     jsonData = response.json()
    # except:
    #     return ""
    # print(jsonData["text"])
    print(response.text)
    try:
        jsonData = response.json()
    except json.decoder.JSONDecodeError:
         return ""    
    time.sleep(1)
    translate_text = jsonData["text"]
    translate_text = translate_text.replace("\"","\'")
    return translate_text


def googletrans(text):
    translate = Translator()
    text = str(text)
    text = text.strip()
    text = text.replace('\\', ' ')
    # try:
    #     translate_text = translate.translate(text=text,dest="en").text
    # except:
    #     return ""
    # translate_text = translate_text.replace("\"","\'")
    try:
        translate_text = translate.translate(text=text,dest="en").text
        translate_text = translate_text.replace("\"","\'")
    except TypeError:
        print('except type error')
        translate_text=""
    except IndexError:
        print('except index error')
        translate_text=""
    print(translate_text)
    return translate_text


def googletrans_list(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('select user_id,item_id,rating,review from review where review != "" and (translate_review is null or translate_review == "") ')
    columns = cur.fetchall()
    text_list = []
    for column in columns[20000:20001]:
        text = str(column[3])
        text = text.strip()
        text = text.replace('\\', ' ')
        text_list.append(text)
    
    text_list = ['私は大学生','ビールが飲みたい']
    print(text_list)
    translator = Translator()
    translations = translator.translate(text_list,dest='ja')
    for translation in translations:
        print(translation.text)

if __name__ == '__main__':
    # main()
    # translate("O jogo que vc pode fazer quase tudo e tem ate fase e parkour esse jogo é muito bom")
    translate_main('steam.db')
    # googletrans('')
    # googletrans_list('steam.db')