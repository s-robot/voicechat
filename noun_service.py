import MeCab

text = "今日の晩御飯何がいいか考えてよ、ソータ"


def noun_list(text: str) -> list[str]:
    tagger = MeCab.Tagger("-Osimple")
    templist: list[str] = tagger.parse(text).split()
    # remove EOS
    templist.pop(-1)
    tempstr = ""
    for i in range(round(len(templist) / 2)):
        if templist[i * 2 + 1] == "名詞-一般":
            tempstr += templist[i * 2]
        else:
            tempstr += "*"
    return [t for t in tempstr.split("*") if t != ""]


print(noun_list(text))
