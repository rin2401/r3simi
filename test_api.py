
# [lấy wordlist]
# https://secureapp.simsimi.com/v1/youngmi/getSearchWordListV2?uid=293125209&av=6.9.1.5&lc=vn&cc=US&tz=Asia%2FJakarta&os=a&ak=j6vOHOjZpjYeEJyPykEF7Uu65CY%3D&word=<>

# [next page]
# https://secureapp.simsimi.com/v1/youngmi/getSearchWordListV2?uid=293125209&av=6.9.1.5&lc=vn&cc=US&tz=Asia%2FJakarta&os=a&ak=j6vOHOjZpjYeEJyPykEF7Uu65CY%3D&word=<>&page=<số>&page_seed=<lấy ở trên>

# [chi tiết câu hỏi - trả lời]
# https://secureapp.simsimi.com/v1/youngmi/getSearchWordDetail?uid=293125209&av=6.9.1.5&lc=vn&cc=US&tz=Asia%2FJakarta&os=a&ak=j6vOHOjZpjYeEJyPykEF7Uu65CY%3D&linkId=<>&logDay=<>

# [api trên lỗi thì chạy cái này 1 lần]
# https://secureapp.simsimi.com/v1/youngmi/saveSearchNextHst?uid=293125209&av=6.9.1.5&lc=vn&cc=US&tz=Asia%2FJakarta&os=a&ak=j6vOHOjZpjYeEJyPykEF7Uu65CY%3D&linkId=<>&logDay=<>&sHstId=<request đầu trả về>&type=O


import requests, json, os, threading, time

def getSearchWordList(word, page, page_seed=None):
    url = "https://secureapp.simsimi.com/v1/youngmi/getSearchWordListV2"
    params = {
        "uid": "293125209",
        "av": "6.9.1.5",
        "lc": "vn",
        "cc": "US",
        "tz": "Asia/Jakarta",
        "os": "a",
        "ak": "j6vOHOjZpjYeEJyPykEF7Uu65CY=",
        "word": word,
        "page": page
    }
    if page_seed:
        params["page_seed"] = page_seed
        
    r = requests.get(url, params=params)
    return r.json()

def getSearchWordDetail(linkId, logDay):
    url = "https://secureapp.simsimi.com/v1/youngmi/getSearchWordDetail"
    params = {
        "uid": "293125209",
        "av": "6.9.1.5",
        "lc": "vn",
        "cc": "US",
        "tz": "Asia/Jakarta",
        "os": "a",
        "ak": "j6vOHOjZpjYeEJyPykEF7Uu65CY=",
        "linkId": linkId,
        "logDay": logDay
    }

    r = requests.get(url, params)

    return r.json()

def getSearchWordListDetailThread(word, page, page_seed=None):
    data = getSearchWordList(word, page, page_seed)
    page_seed = data["page_seed"]
    print(f"{page}/{data['page_total_count']}", data["hits"], len(data["list_data"]), page_seed)
    def parse(d):
        detail = getSearchWordDetail(d["linkId"], d["logDay"])
        for k, v in detail.items():
            d[k] = v
        d["page_seed"] = page_seed
        d["page"] = page
#         print([d["uid"], d["question1"], d["answer"], d["question2"]])
#         time.sleep(0.1)
        
    threads = []
    for d in data["list_data"]:
        thread = threading.Thread(target=parse, args=(d,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
            
    return data

def getSearchWordListDetail(word, page, page_seed=None):
    data = getSearchWordList(word, page, page_seed)
    page_seed = data["page_seed"]
    print(f"{page}/{data['page_total_count']}", data["hits"], len(data["list_data"]), page_seed)
    
    for d in data["list_data"]:
        detail = getSearchWordDetail(d["linkId"], d["logDay"])
        for k, v in detail.items():
            d[k] = v
        d["page_seed"] = page_seed
        d["page"] = page
#         print([d["uid"], d["question1"], d["answer"], d["question2"]])
    return data

def getAllSearchWordListDetail(word):
    page_current = 1
    page_seed = None
    path = f"crawl/{word}.jsonl"
    if os.path.exists(path):
        with open(path, "r", encoding="utf8") as f:
            lines = f.readlines()
        if len(lines) > 0:
            last = json.loads(lines[-1])
            page_current = last["page"] + 1
            page_seed = last["page_seed"]
            print("Continue", word, page_seed, page_current)

    page_total_count = page_current          
    data = None
    page = None
    while page_current <= page_total_count:
        page = getSearchWordListDetailThread(word, page_current, page_seed)
        page_total_count = page["page_total_count"]
        with open(path, "a", encoding="utf8") as f:
            for d in page["list_data"]:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

        if not data:
            data = page
        else: 
            data["list_data"] += page["list_data"]
            data["hits"] += page["hits"]
            data["page_current"] = page["page_current"]
        page_current += 1
        page_total_count = page["page_total_count"]
        page_seed = page["page_seed"]
        
    return data

def talkset(text):
    url = "https://secureapp.simsimi.com/v1/simsimi/talkset"
    params = {
        "uid": "293022127",
        "av": "6.9.1.4",
        "lc": "vn",
        "cc": "US",
        "tz": "Asia/Bangkok",
        "os": "a",
        "ak": "lq/jAFm4PgSOyGNi6yS0iEHeC0g=",
        "message_sentence": text,
        "normalProb": "8",
        "isFilter": "1",
        "talkCnt": "1",
        "talkCntTotal": "30",
        "reqFilter": "1",
        "session": "A8U6yQZPdxMoCh1vuuvqmdphoyS1fYznRmWAbwiVW6LrnKCHoxnUqTTXDqRn3ksG7Q99Abr8toBVBdxDfxY7G5ff",
        "triggerKeywords": "[]"
    }
    
    r = requests.get(url, params)

    return r.json()


if __name__=="__main__":
#     data = getAllSearchWordListDetail("yêu")
    data = talkset("chào bạn")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    