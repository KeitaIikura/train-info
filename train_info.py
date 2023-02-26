from tkinter import *
import tkinter.ttk as ttk
import os
import sys
from dotenv import load_dotenv
import requests
import json

from PIL import Image, ImageTk
from datetime import datetime, timedelta
import time
import threading

# .envファイルを読み込む
load_dotenv()
ACCESS_KEY = os.environ["ACCESS_KEY"]

# アイコン画像の下には取得した文字列をそのまま表示
# メインウィンドウ作成
root = Tk()

# メインウィンドウサイズ
root.geometry("1024x600")

# メインウィンドウタイトル
root.title("info")
# 運行状況API
url_dict = {
    "東西線": f'https://api.odpt.org/api/v4/odpt:TrainInformation?odpt:operator=odpt.Operator:TokyoMetro&odpt:railway=odpt.Railway:TokyoMetro.Tozai&acl:consumerKey={ACCESS_KEY}',
    "半蔵門線": f'https://api.odpt.org/api/v4/odpt:TrainInformation?odpt:operator=odpt.Operator:TokyoMetro&odpt:railway=odpt.Railway:TokyoMetro.Hanzomon&acl:consumerKey={ACCESS_KEY}',
    "都営新宿線": 'https://api-public.odpt.org/api/v4/odpt:TrainInformation?odpt:operator=odpt.Operator:Toei&odpt:railway=odpt.Railway:Toei.Shinjuku'
}
train_list = [
    "東西線", "半蔵門線", "都営新宿線"
]


# MainFrame クラス
class MainFrame(ttk.Frame):
    # コンストラクタ
    def __init__(self, master=None, **kwargs):
        # 親クラスのコンストラクタを呼び出す
        super().__init__(master, **kwargs)

        # create_widgets を呼び出す
        self.create_widgets()

    # ウィジェットを作成
    def create_widgets(self):
        # フレームを作成
        self.frame = Frame(self, bg="#333", bd=0, height=100, relief="flat")

        # フレームを配置
        self.frame.grid(row=0, column=0, columnspan=8, sticky="news")

        # このスクリプトの絶対パス
        self.scr_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        #タイトルの表示
        self.wt=Label(self.frame, text="運行情報", bg="#333", font=("", 40), fg="white")
        self.wt.place(width=200, x=10, y=10)

        self.clock = Label(root, font=("times", 40, "bold"), text="000000")
        self.clock.place(width=420, x=300, y=10)



        # アイコンパス（ディクショナリ）
        self.icon_dict = {
            "tozai": Image.open(self.scr_path + "/img/T.png"),
            "hanzomon": Image.open(self.scr_path + "/img/Z.png"),
            "shinjuku": Image.open(self.scr_path + "/img/TS.png"),
            "normal": Image.open(self.scr_path + "/img/normal.png"),
            "warning": Image.open(self.scr_path + "/img/warning.png"),
        }

        # アイコンサイズを画面サイズにフィット（64x64）させる
        for key, value in self.icon_dict.items():
            self.icon_dict[key] = self.icon_dict[key].resize(
                (64, 64), Image.ANTIALIAS)
            self.icon_dict[key] = ImageTk.PhotoImage(self.icon_dict[key])


        # 路線リスト
        self.wwl = [
            Label(self, text="東西線",  bg="#555", font=("", 30, "bold"), image=self.icon_dict["tozai"], compound=LEFT, width=340, highlightthickness=4, highlightbackground="#009BBF"),
            Label(self, text="半蔵門線",  bg="#555", font=("", 30, "bold"), image=self.icon_dict["hanzomon"], compound=LEFT, width=340, highlightthickness=4, highlightbackground="#8F76D6"),
            Label(self, text="都営新宿",  bg="#555", font=("", 30, "bold"), image=self.icon_dict["shinjuku"], compound=LEFT, width=340, highlightthickness=4, highlightbackground="#B3C146"),
        ]

        # 運行アイコンの初期配置辞書
        self.wwi = [
            Label(self, image=self.icon_dict["normal"], bg="#333"),
            Label(self, image=self.icon_dict["normal"], bg="#333"),
            Label(self, image=self.icon_dict["normal"], bg="#333"),
        ]

        # 路線を配置
        for i in range(len(self.wwl)):
            self.wwl[i].grid(row=1, column=i, sticky="news")


        # 運行アイコンを配置
        for i in range(len(self.wwi)):
            self.wwi[i].grid(row=2, column=i, sticky="news")

        # 運転状況
        self.wwt = [
            Message(self, text="0", bg="#333", fg="white", font=("", 20), width=340),
            Message(self, text="0", bg="#333", fg="white", font=("", 20), width=340),
            Message(self, text="0", bg="#333", fg="white", font=("", 20), width=340),
        ]

        # 運転状況を配置
        for i in range(len(self.wwt)):
            self.wwt[i].grid(row=3, column=i, sticky="news")

        # レイアウト
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        for i in range(len(self.wwl)):
            self.columnconfigure(i, weight=1)


# メインフレームを配置
app = MainFrame(root)
app.pack(side=TOP, expand=1, fill=BOTH)

# メインウィンドウを閉じる
def wm_close():
    root.destroy()


# 閉じるボタン作成
btn = Button(root, text=" X ", font=('', 16), relief=FLAT, command=wm_close)

# 画面がリサイズされたとき

def change_size(event):
    # ボタンの位置を右上に
    btn.place(x=root.winfo_width() - 60, y=14)


# 画面のリサイズをバインドする
root.bind('<Configure>', change_size)


# メインウィンドウの最大化
#root.attributes("-zoom", "1")
# root.attributes("-fullscreen", "1")

# 常に最前面に表示
root.attributes("-topmost", True)

day_of_week = ["月", "火", "水", "木", "金", "土", "日"]
# 時刻取得関数
def tick():
    # 現在時刻取得
    now = datetime.now()
    text = f"{now.year:02}/{now.month:02}/{now.day:02}({day_of_week[now.weekday()]})  {now.hour:02}:{now.minute:02}:{now.second:02}"
    # 時刻設定
    app.clock.config(text=text)
    app.clock.after(1000, tick)
tick()


def update_train_info():
    count = 0
    app.wt
    # 登録路線の運行情報を取得
    for item in train_list:
        res = requests.get(url_dict[item])
        data = json.loads(res.text)
        info_text = data[0]["odpt:trainInformationText"]["ja"]
        print("更新")

        # 運行状況の分岐
        if info_text in ["現在、平常どおり運転しています。" ,"現在、１５分以上の遅延はありません。" ]:
            status = "normal"
            trouble_text="平常運転"
        else:
            status = "warning"
            trouble_text=info_text
        app.wwl[count].configure(text=item)  # 路線名の表示
        # 運行情報アイコンで表示
        app.wwi[count].configure(image=app.icon_dict[status])

        # 運行情報を表示
        app.wwt[count].configure(text="{0}".format(trouble_text),bg="#333")

        # 表示カウンタを更新
        count += 1
    root.after(300000, update_train_info)
    return

# 初回起動
update_train_info()

# メインループ
root.mainloop()