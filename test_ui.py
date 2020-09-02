import os, glob, json, re, time

DIR = "."
os.environ["ANDROID_HOME"] = DIR
print("ANDROID_HOME", os.environ["ANDROID_HOME"])

from uiautomator import device, Selector
import xml.etree.ElementTree as ET

info = device.info
print(json.dumps(info, indent=2, ensure_ascii=False))

def find_id(node, id):
    n = node.find(f".//*[@resource-id='com.ismaker.android.simsimi:id/{id}']")
    if n != None and "text" in n.attrib:
        return n.attrib["text"]
    return None


def click_uix():
    while True:
        root = ET.fromstring(device.dump())
        nodes = root.findall(".//*[@resource-id='com.ismaker.android.simsimi:id/item_search_result_title']")
        if not nodes:
            break
        for i, node in enumerate(nodes[:1]):    
            bounds = list(map(int, re.findall("\d+", node.attrib["bounds"])))
            x = (bounds[2]+bounds[0])//2
            y = (bounds[3]+bounds[1])//2
            device.click(x, y)

def parse_uix(uix):
    root = ET.fromstring(uix)
    nodes = root.findall(".//*[@resource-id='com.ismaker.android.simsimi:id/item_search_result_right_layout']")
    data = []

    for node in nodes:
        question_1 = find_id(node, "item_search_result_dialog_question_1")
        answer = find_id(node, "item_search_result_dialog_answer")
        question_2 = find_id(node, "item_search_result_dialog_question_2")
        user = find_id(node, "item_search_result_nickname")
        loc = find_id(node, "item_search_result_flag")
        time = find_id(node, "item_search_result_time")
        bounds = list(map(int, re.findall("\d+", node.attrib["bounds"])))
        if bounds[-1] >= info["displayHeight"]: continue
        if not (question_1 and answer and question_2 and user): continue
        
        
        texts = [question_1, answer, question_2]
        data.append({
            "texts": texts,
            "user": user,
            "loc": loc,
            "time": time,
            "bounds": bounds
        })
    return data


f = open("crawl_yeu.jsonl", "a", encoding="utf8")

data = []
pre_y = 0
i = 0
while True:
    click_uix()
    page = parse_uix(device.dump())
    if not page:
        continue
    ey = page[-1]["bounds"][-1]
    if ey == pre_y:
        break
    pre_y = ey
    data += page
    for d in page:
        i += 1
        d["id"] = i

        f.write(json.dumps(d, ensure_ascii=False, sort_keys=True)+"\n")
        print(i, d["texts"])
    #d.drag(sx, sy, ex, ey)
    result = device.drag(450, ey - 25, 450, 370)
    print(result)
    if not result:
        break
    time.sleep(0.01)

f.close()

