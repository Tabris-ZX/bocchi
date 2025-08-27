from bocchi.configs.path_config import IMAGE_PATH

SIGN_TODAY_CARD_PATH = IMAGE_PATH / "sign" / "today_card"


lik2relation = {
    "0": "路人",
    "1": "陌生",
    "2": "初识",
    "3": "普通",
    "4": "熟悉",
    "5": "信赖",
    "6": "相知",
    "7": "厚谊",
    "8": "亲密",
}

level2attitude = {
    "0": "排斥",
    "1": "警惕",
    "2": "可以交流",
    "3": "一般",
    "4": "是个好人",
    "5": "好朋友",
    "6": "可以分享小秘密",
    "7": "喜欢",
    "8": "恋人",
}

weekdays = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}

lik2level = {
    2280: "8",
    1390: "7",
    840: "6",
    500: "5",
    290: "4",
    160: "3",
    80: "2",
    30: "1",
    0: "0",
}