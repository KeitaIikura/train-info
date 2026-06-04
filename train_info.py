from tkinter import *
import tkinter.ttk as ttk
import os
import sys
from dotenv import load_dotenv
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime

from src.weather import WeatherInfo

# .envファイルを読み込む
load_dotenv()
ACCESS_KEY = os.environ["ACCESS_KEY"]
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
ZIP_CODE = os.environ["ZIP_CODE"]
REQUEST_TIMEOUT = (5, 15)
WEATHER_UPDATE_INTERVAL_MS = 60000
TRAIN_UPDATE_INTERVAL_MS = 300000
TRAIN_RETRY_INTERVAL_MS = 60000

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
        self.weather = WeatherInfo(WEATHER_API_KEY, timeout=REQUEST_TIMEOUT)
        self.weather_icon = None  # 天気アイコン用の変数
        self.update_weather_info()

    # ウィジェットを作成
    def create_widgets(self):
        # フレームを作成
        self.frame = Frame(self, bg="#333", bd=0, height=100, relief="flat")

        # フレームを配置
        self.frame.grid(row=0, column=0, columnspan=8, sticky="news")

        # このスクリプトの絶対パス
        self.scr_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        # タイトルの表示（見切れないようにフォントを少し小さくする）
        self.wt = Label(self.frame, text="運行情報", bg="#333", font=("", 34), fg="white")
        self.wt.place(width=180, x=10, y=10)

        # 時計を配置（秒まで表示しても見切れないようにフォントと幅を調整）
        self.clock = Label(root, bg="#333", fg="white", font=("times", 32, "bold"), text="000000")
        self.clock.place(width=500, x=230, y=14)

        # 天気を表示（位置は右上）
        self.weather_info = Label(self.frame, text="", bg="#333", font=("", 16), fg="white", justify=LEFT, anchor="w")
        self.weather_info.place(width=200, x=root.winfo_width() - 210, y=10)
        # 天気アイコン用のラベル
        self.weather_icon_label = Label(self.frame, bg="#333")
        self.weather_icon_label.place(x=root.winfo_width() - 270, y=10)



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
                (64, 64), Image.LANCZOS)
            self.icon_dict[key] = ImageTk.PhotoImage(self.icon_dict[key])


        # 路線リスト
        self.wwl = [
            Label(self, text="東西線",  bg="#555", fg="white", font=("", 30, "bold"), image=self.icon_dict["tozai"], compound=LEFT, width=340, highlightthickness=4, highlightbackground="#009BBF"),
            Label(self, text="半蔵門線",  bg="#555", fg="white", font=("", 30, "bold"), image=self.icon_dict["hanzomon"], compound=LEFT, width=340, highlightthickness=4, highlightbackground="#8F76D6"),
            Label(self, text="都営新宿線",  bg="#555", fg="white", font=("", 30, "bold"), image=self.icon_dict["shinjuku"], compound=LEFT, width=340, highlightthickness=4, highlightbackground="#B3C146"),
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

        # 余白表示（他情報表示予定）
        for i in range(3):
            Message(self, bg="#333", fg="white", font=("", 20), width=340).grid(row=4, column=i, sticky="news")

        # レイアウト
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        for i in range(len(self.wwl)):
            self.columnconfigure(i, weight=1)

    def update_weather_info(self):
        try:
            weather_data = self.weather.get_current_weather(ZIP_CODE)
            weather_text = (f"気温: {weather_data.temp:.1f}°C\n"
                            f"最高: {weather_data.temp_max:.1f}°C\n"
                            f"最低: {weather_data.temp_min:.1f}°C\n"
                            f"湿度: {weather_data.humidity}%\n"
                            f"風速: {weather_data.wind_speed}m/s\n"
                            f"風向: {weather_data.wind_deg}")
            self.weather_info.config(text=weather_text)

            # アイコンを取得して表示
            try:
                response = requests.get(weather_data.icon_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                img = img.resize((50, 50), Image.LANCZOS)  # アイコンサイズを調整
                self.weather_icon = ImageTk.PhotoImage(img)
                self.weather_icon_label.config(image=self.weather_icon)
                self.weather_icon_label.image = self.weather_icon  # 参照を保持
            except (requests.RequestException, OSError) as e:
                print(f"天気アイコンの取得に失敗: {e}")
                self.weather_icon_label.config(image="")
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            print(f"天気情報の更新に失敗: {e}")
            self.weather_info.config(text="天気情報を取得できません")
            self.weather_icon_label.config(image="")
        finally:
            self.after(WEATHER_UPDATE_INTERVAL_MS, self.update_weather_info)  # 1分ごとに更新・失敗時も再試行

    def on_resize(self, event):
        # ウィンドウサイズが変更されたときに天気情報の位置を調整
        self.weather_info.place(width=200, x=self.winfo_width() - 210, y=10)
        self.weather_icon_label.place(x=self.winfo_width() - 270, y=10)  # アイコンの位置も調整


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
root.bind('<Configure>', lambda e: (change_size(e), app.on_resize(e)))


# メインウィンドウの最大化
# root.attributes("-zoom", "1")
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

def update_train_info():
    has_error = False

    # 登録路線の運行情報を取得
    for count, item in enumerate(train_list):
        try:
            res = requests.get(url_dict[item], timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            data = res.json()
            info_text = data[0]["odpt:trainInformationText"]["ja"]
            print(f'{item}: 更新')

            # 運行状況の分岐
            if info_text in ["現在、平常どおり運転しています。" ,"現在、１５分以上の遅延はありません。" ]:
                status = "normal"
                trouble_text="平常運転"
            else:
                status = "warning"
                trouble_text=info_text
        except (requests.RequestException, ValueError, KeyError, IndexError) as e:
            has_error = True
            print(f"{item}: 運行情報の更新に失敗: {e}")
            status = "warning"
            trouble_text = "運行情報を取得できません（次回自動再試行）"

        app.wwl[count].configure(text=item)  # 路線名の表示
        # 運行情報アイコンで表示
        app.wwi[count].configure(image=app.icon_dict[status])

        # 運行情報を表示
        app.wwt[count].configure(text="{0}".format(trouble_text),bg="#333")

    next_interval = TRAIN_RETRY_INTERVAL_MS if has_error else TRAIN_UPDATE_INTERVAL_MS
    root.after(next_interval, update_train_info)
    return


# 初回起動
tick()
update_train_info()

# メインループ
root.mainloop()