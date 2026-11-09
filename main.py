import json
import os
import platform
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp


def setup_chinese_font():
    system = platform.system()
    font_paths = []

    if system == "Windows":
        candidates = [
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "msyh.ttc"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "simhei.ttf"),
            os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "simsun.ttc"),
        ]
        font_paths = [f for f in candidates if os.path.exists(f)]
    elif system == "Linux":
        linux_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf",
        ]
        font_paths = [f for f in linux_fonts if os.path.exists(f)]
    elif system == "Darwin":
        mac_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
        font_paths = [f for f in mac_fonts if os.path.exists(f)]

    if font_paths:
        try:
            LabelBase.register(name="Chinese", fn_regular=font_paths[0])
            print(f"[INFO] 使用中文字体: {font_paths[0]}")
            return True
        except Exception as e:
            print(f"[WARN] 中文字体注册失败: {e}")

    print("[WARN] 未找到中文字体，将使用默认字体")
    return False


FONT_NAME = "Chinese" if setup_chinese_font() else ""

DATA_FILE = os.path.join(os.path.expanduser("~"), "expenses.json")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class AddScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            self.bg = Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self._update_bg, size=self._update_bg)

        title = Label(
            text="记一笔",
            font_size=dp(28),
            font_name=FONT_NAME,
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"x": 0, "top": 1},
        )
        self.layout.add_widget(title)

        form = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=[dp(30), dp(10), dp(30), dp(10)],
            size_hint=(1, 0.55),
            pos_hint={"x": 0, "top": 0.88},
        )

        form.add_widget(
            Label(
                text="金额（元）",
                font_size=dp(18),
                font_name=FONT_NAME,
                color=(0.4, 0.4, 0.4, 1),
                size_hint=(1, None),
                height=dp(30),
                halign="left",
                valign="middle",
            )
        )
        self.amount_input = TextInput(
            hint_text="0.00",
            input_filter="float",
            font_size=dp(26),
            font_name=FONT_NAME,
            size_hint=(1, None),
            height=dp(55),
            multiline=False,
        )
        form.add_widget(self.amount_input)

        form.add_widget(
            Label(
                text="备注（如：午餐、打车）",
                font_size=dp(18),
                font_name=FONT_NAME,
                color=(0.4, 0.4, 0.4, 1),
                size_hint=(1, None),
                height=dp(30),
                halign="left",
                valign="middle",
            )
        )
        self.note_input = TextInput(
            hint_text="今天花了什么？",
            font_size=dp(20),
            font_name=FONT_NAME,
            size_hint=(1, None),
            height=dp(55),
            multiline=False,
        )
        form.add_widget(self.note_input)

        self.layout.add_widget(form)

        btn_row = BoxLayout(
            spacing=dp(20),
            padding=[dp(30), 0, dp(30), 0],
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"x": 0, "top": 0.3},
        )

        save_btn = Button(
            text="✓ 保存",
            font_size=dp(22),
            font_name=FONT_NAME,
            background_color=(0.18, 0.55, 0.34, 1),
            background_normal="",
        )
        save_btn.bind(on_press=self.save_expense)
        btn_row.add_widget(save_btn)

        back_btn = Button(
            text="← 返回",
            font_size=dp(22),
            font_name=FONT_NAME,
            background_color=(0.6, 0.6, 0.6, 1),
            background_normal="",
        )
        back_btn.bind(
            on_press=lambda x: self._go_home()
        )
        btn_row.add_widget(back_btn)

        self.layout.add_widget(btn_row)
        self.add_widget(self.layout)

    def _update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def _go_home(self):
        self.amount_input.text = ""
        self.note_input.text = ""
        self.manager.current = "home"

    def save_expense(self, instance):
        amount_text = self.amount_input.text.strip()
        if not amount_text:
            popup = Popup(
                title="提示",
                content=Label(text="请输入金额！", font_name=FONT_NAME),
                size_hint=(0.7, 0.3),
            )
            popup.open()
            return

        amount = float(amount_text)
        if amount <= 0:
            popup = Popup(
                title="提示",
                content=Label(text="金额必须大于0！", font_name=FONT_NAME),
                size_hint=(0.7, 0.3),
            )
            popup.open()
            return

        note = self.note_input.text.strip() or "日常支出"
        now = datetime.now()

        data = load_data()
        data.append(
            {
                "amount": amount,
                "note": note,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M"),
            }
        )
        save_data(data)

        self.amount_input.text = ""
        self.note_input.text = ""

        popup = Popup(
            title="成功",
            content=Label(text=f"已记录：{note} ¥{amount:.2f}", font_name=FONT_NAME),
            size_hint=(0.8, 0.35),
        )
        popup.open()

        self.manager.get_screen("home").refresh()
        self.manager.current = "home"


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()

        with self.layout.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            self.bg = Rectangle(pos=self.layout.pos, size=self.layout.size)
        self.layout.bind(pos=self._update_bg, size=self._update_bg)

        self.filter_mode = "all"
        self.start_date = ""
        self.end_date = ""

        filter_bar = BoxLayout(
            orientation="horizontal",
            spacing=dp(5),
            padding=[dp(10), dp(5), dp(10), dp(5)],
            size_hint=(1, None),
            height=dp(40),
            pos_hint={"x": 0, "top": 1},
        )

        for mode, btn_text in [("today", "今天"), ("week", "本周"), ("month", "本月"), ("payroll", "月结"), ("all", "全部")]:
            btn = Button(
                text=btn_text,
                font_size=dp(13),
                font_name=FONT_NAME,
                size_hint_x=None,
                width=dp(60),
                background_color=(0.7, 0.75, 0.8, 1),
                background_normal="",
                color=(0.4, 0.45, 0.5, 1),
            )
            btn.bind(on_press=lambda x, m=mode: self.set_filter(m))
            filter_bar.add_widget(btn)

        custom_btn = Button(
            text="自定义",
            font_size=dp(14),
            font_name=FONT_NAME,
            size_hint_x=None,
            width=dp(70),
            background_color=(0.6, 0.65, 0.75, 1),
            background_normal="",
            color=(0.35, 0.4, 0.5, 1),
        )
        custom_btn.bind(on_press=self.show_custom_filter)
        filter_bar.add_widget(custom_btn)

        self.filter_bar = filter_bar
        self.filter_buttons = list(filter_bar.children)
        self.layout.add_widget(filter_bar)

        self.total_label = Label(
            text="",
            font_size=dp(22),
            font_name=FONT_NAME,
            bold=True,
            color=(0.85, 0.2, 0.2, 1),
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"x": 0, "top": 0.92},
            halign="center",
            valign="middle",
        )
        self.layout.add_widget(self.total_label)

        self.date_range_label = Label(
            text="",
            font_size=dp(13),
            font_name=FONT_NAME,
            color=(0.55, 0.55, 0.55, 1),
            size_hint=(1, None),
            height=dp(25),
            pos_hint={"x": 0, "top": 0.85},
            halign="center",
            valign="middle",
        )
        self.layout.add_widget(self.date_range_label)

        self.count_label = Label(
            text="",
            font_size=dp(15),
            font_name=FONT_NAME,
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(1, None),
            height=dp(28),
            pos_hint={"x": 0, "top": 0.80},
            halign="center",
            valign="middle",
        )
        self.layout.add_widget(self.count_label)

        self.scroll = ScrollView(
            size_hint=(1, 0.60),
            pos_hint={"x": 0, "top": 0.77},
        )
        self.list_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(15), dp(5), dp(15), dp(5)],
            size_hint_y=None,
        )
        self.list_layout.bind(
            minimum_height=self.list_layout.setter("height")
        )
        self.scroll.add_widget(self.list_layout)
        self.layout.add_widget(self.scroll)

        btn_row = BoxLayout(
            spacing=dp(15),
            padding=[dp(20), dp(5), dp(20), dp(5)],
            size_hint=(1, None),
            height=dp(65),
            pos_hint={"x": 0, "y": 0},
        )

        add_btn = Button(
            text="+ 记一笔",
            font_size=dp(24),
            font_name=FONT_NAME,
            background_color=(0.18, 0.55, 0.34, 1),
            background_normal="",
        )
        add_btn.bind(
            on_press=lambda x: setattr(self.manager, "current", "add")
        )
        btn_row.add_widget(add_btn)

        clear_btn = Button(
            text="清空",
            font_size=dp(20),
            font_name=FONT_NAME,
            background_color=(0.85, 0.25, 0.25, 1),
            background_normal="",
            size_hint=(0.4, 1),
        )
        clear_btn.bind(on_press=self.confirm_clear)
        btn_row.add_widget(clear_btn)

        self.layout.add_widget(btn_row)
        self.add_widget(self.layout)

    def _update_bg(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size

    def set_filter(self, mode):
        self.filter_mode = mode
        today = datetime.now().strftime("%Y-%m-%d")
        
        if mode == "today":
            self.start_date = today
            self.end_date = today
        elif mode == "week":
            now = datetime.now()
            start_of_week = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
            self.start_date = start_of_week
            self.end_date = today
        elif mode == "month":
            now = datetime.now()
            start_of_month = now.replace(day=1).strftime("%Y-%m-%d")
            self.start_date = start_of_month
            self.end_date = today
        elif mode == "payroll":
            now = datetime.now()
            day = now.day
            if day >= 15:
                start = now.replace(day=15)
                next_month = now.replace(day=28) + timedelta(days=4)
                end = next_month.replace(day=15)
            else:
                prev_month = now.replace(day=1) - timedelta(days=1)
                start = prev_month.replace(day=15)
                end = now.replace(day=15)
            self.start_date = start.strftime("%Y-%m-%d")
            self.end_date = end.strftime("%Y-%m-%d")
        else:
            self.start_date = ""
            self.end_date = ""

        for btn in self.filter_buttons:
            btn.background_color = (0.7, 0.75, 0.8, 1)
            btn.color = (0.4, 0.45, 0.5, 1)

        btn_map = {"今天": "today", "本周": "week", "本月": "month", "月结": "payroll", "全部": "all"}
        for btn in self.filter_buttons:
            if btn.text in btn_map and btn_map[btn.text] == mode:
                btn.background_color = (0.18, 0.55, 0.34, 1)
                btn.color = (1, 1, 1, 1)

        self.refresh()

    def show_custom_filter(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(15))
        
        date_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        date_row.add_widget(Label(text="开始日期:", font_size=dp(16), font_name=FONT_NAME, size_hint_x=None))
        self.start_input = TextInput(
            hint_text="YYYY-MM-DD",
            font_size=dp(16),
            font_name=FONT_NAME,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
        )
        date_row.add_widget(self.start_input)
        content.add_widget(date_row)

        end_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        end_row.add_widget(Label(text="结束日期:", font_size=dp(16), font_name=FONT_NAME, size_hint_x=None))
        self.end_input = TextInput(
            hint_text="YYYY-MM-DD",
            font_size=dp(16),
            font_name=FONT_NAME,
            multiline=False,
            size_hint_y=None,
            height=dp(45),
        )
        end_row.add_widget(self.end_input)
        content.add_widget(end_row)

        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        ok_btn = Button(text="确定", font_name=FONT_NAME, background_color=(0.18, 0.55, 0.34, 1), background_normal="")
        cancel_btn = Button(text="取消", font_name=FONT_NAME, background_color=(0.6, 0.6, 0.6, 1), background_normal="")
        btn_row.add_widget(ok_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)

        popup = Popup(title="自定义日期范围", content=content, size_hint=(0.85, 0.4))

        def apply_custom(x):
            popup.dismiss()
            start = self.start_input.text.strip()
            end = self.end_input.text.strip()
            
            try:
                datetime.strptime(start, "%Y-%m-%d")
                datetime.strptime(end, "%Y-%m-%d")
                
                self.filter_mode = "custom"
                self.start_date = start
                self.end_date = end
                
                for btn in self.filter_buttons:
                    btn.background_color = (0.7, 0.75, 0.8, 1)
                    btn.color = (0.4, 0.45, 0.5, 1)
                
                self.refresh()
            except ValueError:
                error_popup = Popup(
                    title="错误",
                    content=Label(text="日期格式不正确！\n请使用 YYYY-MM-DD 格式", font_name=FONT_NAME),
                    size_hint=(0.7, 0.3),
                )
                error_popup.open()

        ok_btn.bind(on_press=apply_custom)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

    def refresh(self):
        data = load_data()
        
        filtered_data = []
        if self.filter_mode != "all" or (self.start_date and self.end_date):
            for item in data:
                item_date = item["date"]
                if self.start_date <= item_date <= self.end_date:
                    filtered_data.append(item)
        else:
            filtered_data = data

        self.list_layout.clear_widgets()

        total = sum(item["amount"] for item in filtered_data)
        self.total_label.text = f"总支出：¥{total:.2f}"
        self.count_label.text = f"共 {len(filtered_data)} 笔记录"

        if self.filter_mode == "custom":
            self.date_range_label.text = f"{self.start_date} 至 {self.end_date}"
        elif self.filter_mode == "today":
            self.date_range_label.text = "今日"
        elif self.filter_mode == "week":
            self.date_range_label.text = f"{self.start_date} 至 {self.end_date}（本周）"
        elif self.filter_mode == "month":
            self.date_range_label.text = f"{self.start_date} 至 {self.end_date}（本月）"
        elif self.filter_mode == "payroll":
            self.date_range_label.text = f"{self.start_date} 至 {self.end_date}（月结周期）"
        else:
            self.date_range_label.text = "所有时间"

        if not filtered_data:
            self.list_layout.add_widget(
                Label(
                    text="该时间段没有记录\n点击下方「+ 记一笔」开始记账",
                    font_size=dp(18),
                    font_name=FONT_NAME,
                    color=(0.6, 0.6, 0.6, 1),
                    halign="center",
                    size_hint_y=None,
                    height=dp(200),
                )
            )
            return

        from collections import OrderedDict
        sorted_data = sorted(filtered_data, key=lambda x: (x["date"], x["time"]), reverse=True)
        
        date_groups = OrderedDict()
        for item in sorted_data:
            date_str = item["date"]
            if date_str not in date_groups:
                date_groups[date_str] = []
            date_groups[date_str].append(item)

        for date_str, items in date_groups.items():
            day_total = sum(item["amount"] for item in items)
            
            date_header = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(50),
                padding=[dp(15), dp(8), dp(15), dp(5)],
            )
            
            with date_header.canvas.before:
                Color(0.88, 0.9, 0.93, 1)
                header_bg = Rectangle(pos=date_header.pos, size=date_header.size)
            date_header.bind(
                pos=lambda i, v, bg=header_bg: setattr(bg, "pos", v),
                size=lambda i, v, bg=header_bg: setattr(bg, "size", v),
            )
            
            header_row = BoxLayout(size_hint_y=None, height=dp(25))
            
            weekday_map = {
                "Monday": "周一", "Tuesday": "周二", "Wednesday": "周三",
                "Thursday": "周四", "Friday": "周五", "Saturday": "周六", "Sunday": "周日"
            }
            try:
                from datetime import datetime as dt
                dt_obj = dt.strptime(date_str, "%Y-%m-%d")
                weekday = weekday_map.get(dt_obj.strftime("%A"), "")
                display_date = f"{date_str}  {weekday}"
            except Exception:
                display_date = date_str
            
            header_row.add_widget(
                Label(
                    text=display_date,
                    font_size=dp(16),
                    font_name=FONT_NAME,
                    bold=True,
                    color=(0.3, 0.3, 0.3, 1),
                    halign="left",
                    valign="middle",
                )
            )
            header_row.add_widget(
                Label(
                    text=f"当日: ¥{day_total:.2f}",
                    font_size=dp(16),
                    font_name=FONT_NAME,
                    bold=True,
                    color=(0.85, 0.25, 0.25, 1),
                    halign="right",
                    valign="middle",
                )
            )
            date_header.add_widget(header_row)
            
            count_text = Label(
                text=f"{len(items)} 笔",
                font_size=dp(12),
                font_name=FONT_NAME,
                color=(0.65, 0.65, 0.65, 1),
                halign="left",
                size_hint_y=None,
                height=dp(17),
            )
            date_header.add_widget(count_text)
            
            self.list_layout.add_widget(date_header)

            for item in items:
                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(60),
                    spacing=dp(10),
                    padding=[dp(20), dp(4), dp(15), dp(4)],
                )

                with row.canvas.before:
                    Color(1, 1, 1, 1)
                    row_bg = Rectangle(pos=row.pos, size=row.size)
                row.bind(
                    pos=lambda i, v, bg=row_bg: setattr(bg, "pos", v),
                    size=lambda i, v, bg=row_bg: setattr(bg, "size", v),
                )

                info = BoxLayout(orientation="vertical", padding=[dp(5), dp(3), 0, dp(3)])
                info.add_widget(
                    Label(
                        text=item["note"],
                        font_size=dp(17),
                        font_name=FONT_NAME,
                        color=(0.2, 0.2, 0.2, 1),
                        halign="left",
                        valign="middle",
                        size_hint_y=0.7,
                    )
                )
                info.add_widget(
                    Label(
                        text=item["time"],
                        font_size=dp(13),
                        font_name=FONT_NAME,
                        color=(0.6, 0.6, 0.6, 1),
                        halign="left",
                        valign="middle",
                        size_hint_y=0.3,
                    )
                )
                row.add_widget(info)

                amount_label = Label(
                    text=f'-¥{item["amount"]:.2f}',
                    font_size=dp(19),
                    font_name=FONT_NAME,
                    bold=True,
                    color=(0.85, 0.2, 0.2, 1),
                    halign="right",
                    valign="center",
                    size_hint_x=0.45,
                )
                row.add_widget(amount_label)

                self.list_layout.add_widget(row)

    def confirm_clear(self, instance):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))
        content.add_widget(
            Label(text="确定清空所有记录？\n此操作不可恢复！", font_name=FONT_NAME, halign="center")
        )

        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        yes = Button(text="确定", font_name=FONT_NAME, background_color=(0.85, 0.25, 0.25, 1), background_normal="")
        no = Button(text="取消", font_name=FONT_NAME, background_color=(0.6, 0.6, 0.6, 1), background_normal="")
        btn_row.add_widget(yes)
        btn_row.add_widget(no)
        content.add_widget(btn_row)

        popup = Popup(title="确认", content=content, size_hint=(0.75, 0.35))
        yes.bind(on_press=lambda x: self._do_clear(popup))
        no.bind(on_press=popup.dismiss)
        popup.open()

    def _do_clear(self, popup):
        popup.dismiss()
        save_data([])
        self.refresh()


class ExpenseApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.97, 1)
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddScreen(name="add"))
        sm.current = "home"
        return sm

    def on_start(self):
        self.root.get_screen("home").refresh()


if __name__ == "__main__":
    ExpenseApp().run()