# -*- coding: utf-8 -*-

"""
NAIMI BOOK
Kivy - Persian RTL / English LTR
Public-domain books from Gutendex / Project Gutenberg
"""

import os
import re
import json
import time
import threading
import urllib.request
import urllib.parse
import subprocess

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup


# =========================================================
# OPTIONAL RTL SUPPORT
# =========================================================

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    RTL_OK = True
except Exception:
    RTL_OK = False


# =========================================================
# OPTIONAL PDF SUPPORT
# =========================================================

try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4
    REPORTLAB_OK = True
except Exception:
    REPORTLAB_OK = False


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GUTENDEX_URL = "https://gutendex.com/books/"

FONT_NAMES = [
    "NotoNaskhArabic-Regular.ttf",
    "NotoSansArabic-Regular.ttf",
    "NotoSansArabicUI-Regular.ttf",
    "NotoNaskhArabicUI-Regular.ttf",
]

SYSTEM_FONTS = [
    "/system/fonts/NotoNaskhArabic-Regular.ttf",
    "/system/fonts/NotoSansArabic-Regular.ttf",
    "/system/fonts/NotoSansArabicUI-Regular.ttf",
    "/system/fonts/DroidNaskh-Regular.ttf",
]


def find_font():
    for name in FONT_NAMES:
        path = os.path.join(BASE_DIR, name)
        if os.path.isfile(path):
            return path

    for path in SYSTEM_FONTS:
        if os.path.isfile(path):
            return path

    return None


ARABIC_FONT = find_font()
PDF_FONT_NAME = None


# =========================================================
# PERSIAN / ARABIC DETECTION
# =========================================================

ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]"
)


def has_persian(text):
    return bool(ARABIC_RE.search(str(text)))


def rtl_text(text):
    """
    Converts Persian/Arabic text into a visually correct
    string for Kivy labels.
    """

    text = str(text)

    if not text:
        return ""

    if not has_persian(text):
        return text

    if not RTL_OK:
        return text

    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def ui_text(text, language):
    """
    Persian -> visual RTL
    English -> normal LTR
    """

    if language == "fa":
        return rtl_text(text)

    return str(text)


# =========================================================
# TRANSLATIONS
# =========================================================

UI = {

    "fa": {

        "app": "کتابخانه نعیمی",
        "search": "جستجو",
        "search_hint": "نام کتاب یا موضوع را جستجو کنید",

        "library": "کتابخانه",
        "settings": "تنظیمات",
        "history": "تاریخچه",
        "favorites": "علاقه‌مندی‌ها",
        "translated": "ترجمه‌شده‌ها",

        "back": "برگشت",
        "open": "باز کردن",
        "details": "جزئیات کتاب",

        "author": "نویسنده",
        "language": "زبان",
        "downloads": "دانلودها",
        "public_domain": "دامنه عمومی",

        "favorite": "علاقه‌مندی",
        "download_txt": "دانلود متن",
        "create_pdf": "ساخت PDF",
        "translate": "ترجمه به فارسی",

        "searching": "در حال جستجو...",
        "no_results": "کتابی پیدا نشد.",
        "books_found": "کتاب پیدا شد",

        "download": "در حال دانلود...",
        "download_complete": "دانلود کامل شد",

        "translation": "ترجمه فارسی",
        "translation_start": "در حال شروع ترجمه...",
        "translation_complete": "ترجمه کامل شد",
        "translation_failed": "ترجمه انجام نشد",

        "history_empty": "تاریخچه خالی است.",
        "favorites_empty": "علاقه‌مندی‌ها خالی است.",
        "translated_empty": "هنوز کتابی ترجمه نشده است.",

        "clear": "پاک کردن بخش فعلی",

        "language_setting": "زبان برنامه",
        "persian": "فارسی",
        "english": "English",

        "save": "ذخیره",
        "saved": "ذخیره شد",

        "about": "درباره برنامه",
        "download_folder": "پوشه دانلود",

        "pdf_support": "بررسی پشتیبانی PDF",

        "book_ready": "جزئیات کتاب آماده است.",
        "please_search": "لطفاً نام کتاب را وارد کنید.",

        "error": "خطا",
        "ok": "تأیید",

        "open_txt": "باز کردن TXT",
        "open_pdf": "باز کردن PDF",

        "nothing": "چیزی وجود ندارد.",
    },

    "en": {

        "app": "NAIMI BOOK",
        "search": "Search",
        "search_hint": "Search for a book or topic",

        "library": "Library",
        "settings": "Settings",
        "history": "History",
        "favorites": "Favorites",
        "translated": "Translated",

        "back": "Back",
        "open": "Open",
        "details": "Book Details",

        "author": "Author",
        "language": "Language",
        "downloads": "Downloads",
        "public_domain": "Public Domain",

        "favorite": "Favorite",
        "download_txt": "Download TXT",
        "create_pdf": "Create PDF",
        "translate": "Translate to Persian",

        "searching": "Searching...",
        "no_results": "No books found.",
        "books_found": "books found",

        "download": "Downloading...",
        "download_complete": "Download complete",

        "translation": "Persian Translation",
        "translation_start": "Starting translation...",
        "translation_complete": "Translation complete",
        "translation_failed": "Translation failed",

        "history_empty": "History is empty.",
        "favorites_empty": "Favorites are empty.",
        "translated_empty": "No translated books yet.",

        "clear": "Clear Current Section",

        "language_setting": "App Language",
        "persian": "فارسی",
        "english": "English",

        "save": "Save",
        "saved": "Saved",

        "about": "About",
        "download_folder": "Download Folder",

        "pdf_support": "Check PDF Support",

        "book_ready": "Book details ready.",
        "please_search": "Please enter a book name.",

        "error": "Error",
        "ok": "OK",

        "open_txt": "Open TXT",
        "open_pdf": "Open PDF",

        "nothing": "Nothing here.",
    }
}


# =========================================================
# POPUP
# =========================================================

def show_popup(title, message):

    def create(_dt):

        try:

            root = BoxLayout(
                orientation="vertical",
                padding=dp(15),
                spacing=dp(10)
            )

            label = Label(
                text=rtl_text(message),
                halign="center",
                valign="middle"
            )

            label.bind(
                size=lambda obj, value:
                setattr(obj, "text_size", value)
            )

            button = Button(
                text="OK",
                size_hint_y=None,
                height=dp(48)
            )

            root.add_widget(label)
            root.add_widget(button)

            popup = Popup(
                title=str(title),
                content=root,
                size_hint=(0.9, 0.5)
            )

            button.bind(
                on_release=popup.dismiss
            )

            popup.open()

        except Exception as e:
            print("POPUP ERROR:", e)

    Clock.schedule_once(create, 0)


# =========================================================
# DOWNLOAD FOLDER
# =========================================================

def get_download_folder():

    candidates = [

        "/storage/emulated/0/Download/Naimi Book",

        "/sdcard/Download/Naimi Book",
    ]

    try:

        app = App.get_running_app()

        candidates.append(
            os.path.join(
                app.user_data_dir,
                "Naimi Book"
            )
        )

    except Exception:
        pass

    candidates.append(
        os.path.join(
            BASE_DIR,
            "Naimi Book"
        )
    )

    for folder in candidates:

        try:

            os.makedirs(
                folder,
                exist_ok=True
            )

            test_file = os.path.join(
                folder,
                ".naimi_test"
            )

            with open(
                test_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.write("ok")

            try:
                os.remove(test_file)
            except Exception:
                pass

            return folder

        except Exception:
            continue

    return BASE_DIR


# =========================================================
# SAFE FILE NAME
# =========================================================

def safe_filename(name):

    name = str(name)

    name = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    name = name.strip()

    if not name:
        name = "book"

    return name[:150]


# =========================================================
# NETWORK
# =========================================================

def http_get(url, timeout=60):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0 (Android; NaimiBook/7.0)",
            "Accept":
                "*/*"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout
    ) as response:

        return response.read()


def get_json(url, timeout=60):

    data = http_get(
        url,
        timeout
    )

    return json.loads(
        data.decode(
            "utf-8",
            errors="replace"
        )
    )


# =========================================================
# BOOK HELPERS
# =========================================================

def author_name(book):

    authors = book.get(
        "authors",
        []
    )

    names = []

    for author in authors:

        name = author.get(
            "name",
            ""
        )

        if name:
            names.append(name)

    if names:
        return ", ".join(names)

    return "Unknown Author"


def text_url(book):

    formats = book.get(
        "formats",
        {}
    )

    preferred = [

        "text/plain; charset=utf-8",

        "text/plain",

        "text/plain; charset=us-ascii",
    ]

    for key in preferred:

        if key in formats:
            return formats[key]

    for key, value in formats.items():

        if str(key).startswith(
            "text/plain"
        ):
            return value

    return None


def cover_url(book):

    return book.get(
        "formats",
        {}
    ).get(
        "image/jpeg"
    )


def simple_book(book):

    return {

        "id":
            book.get("id"),

        "title":
            book.get(
                "title",
                "Untitled"
            ),

        "authors":
            book.get(
                "authors",
                []
            ),

        "languages":
            book.get(
                "languages",
                []
            ),

        "formats":
            book.get(
                "formats",
                {}
            ),

        "download_count":
            book.get(
                "download_count",
                0
            ),

        "copyright":
            book.get(
                "copyright"
            ),
    }


# =========================================================
# STORAGE
# =========================================================

class Storage:

    def __init__(self):

        app = App.get_running_app()

        self.path = os.path.join(
            app.user_data_dir,
            "books.json"
        )

        self.data = {

            "history": [],

            "favorites": [],

            "translated": [],
        }

        self.load()

    def load(self):

        try:

            if not os.path.isfile(
                self.path
            ):
                return

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            for key in self.data:

                if isinstance(
                    data.get(key),
                    list
                ):
                    self.data[key] = data[key]

        except Exception as e:

            print(
                "STORAGE LOAD ERROR:",
                e
            )

    def save(self):

        try:

            folder = os.path.dirname(
                self.path
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            with open(
                self.path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception as e:

            print(
                "STORAGE SAVE ERROR:",
                e
            )

    def add_history(self, book):

        items = self.data[
            "history"
        ]

        items = [

            x for x in items

            if x.get("id")
            != book.get("id")
        ]

        items.insert(
            0,
            book
        )

        self.data[
            "history"
        ] = items[:100]

        self.save()

    def is_favorite(self, book):

        return any(
            x.get("id")
            == book.get("id")

            for x in self.data[
                "favorites"
            ]
        )

    def toggle_favorite(self, book):

        if self.is_favorite(book):

            self.data[
                "favorites"
            ] = [

                x for x in self.data[
                    "favorites"
                ]

                if x.get("id")
                != book.get("id")
            ]

            result = False

        else:

            self.data[
                "favorites"
            ].insert(
                0,
                book
            )

            result = True

        self.save()

        return result


# =========================================================
# TRANSLATE SEARCH QUERY
# =========================================================

def translate_query_to_english(query):

    query = str(query).strip()

    if not query:
        return ""

    if not has_persian(query):
        return query

    try:

        encoded = urllib.parse.quote(
            query
        )

        url = (
            "https://translate.googleapis.com/"
            "translate_a/single"
            "?client=gtx"
            "&sl=fa"
            "&tl=en"
            "&dt=t"
            "&q="
            + encoded
        )

        data = http_get(
            url,
            timeout=25
        )

        obj = json.loads(
            data.decode(
                "utf-8",
                errors="replace"
            )
        )

        result = []

        for item in obj[0]:

            if item and item[0]:
                result.append(
                    item[0]
                )

        translated = "".join(
            result
        ).strip()

        return translated or query

    except Exception as e:

        print(
            "QUERY TRANSLATION:",
            e
        )

        return query


# =========================================================
# HOME SCREEN
# =========================================================

class HomeScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(
            name="home",
            **kwargs
        )

        self.app = App.get_running_app()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        self.title_label = Label(
            bold=True,
            font_size=dp(24),
            size_hint_y=None,
            height=dp(52)
        )

        root.add_widget(
            self.title_label
        )

        self.search_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(52)
        )

        root.add_widget(
            self.search_input
        )

        controls = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        self.search_button = Button()

        self.library_button = Button()

        self.settings_button = Button()

        self.search_button.bind(
            on_release=lambda x:
            self.search()
        )

        self.library_button.bind(
            on_release=lambda x:
            self.open_library()
        )

        self.settings_button.bind(
            on_release=lambda x:
            self.open_settings()
        )

        controls.add_widget(
            self.search_button
        )

        controls.add_widget(
            self.library_button
        )

        controls.add_widget(
            self.settings_button
        )

        root.add_widget(
            controls
        )

        self.status = Label(
            size_hint_y=None,
            height=dp(35)
        )

        root.add_widget(
            self.status
        )

        scroll = ScrollView()

        self.results = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )

        self.results.bind(
            minimum_height=
            self.results.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.results
        )

        root.add_widget(
            scroll
        )

        self.add_widget(root)

        self.update_language()

    def update_language(self):

        self.title_label.text = ui_text(
            self.tr("app"),
            self.app.language
        )

        self.search_input.hint_text = (
            self.tr("search_hint")
        )

        self.search_button.text = (
            self.tr("search")
        )

        self.library_button.text = (
            self.tr("library")
        )

        self.settings_button.text = (
            self.tr("settings")
        )

        self.status.text = (
            self.tr("search_hint")
        )

    def tr(self, key):

        return self.app.tr(key)

    def search(self):

        query = self.search_input.text.strip()

        if not query:

            show_popup(
                self.tr("error"),
                self.tr("please_search")
            )

            return

        self.results.clear_widgets()

        self.status.text = (
            self.tr("searching")
        )

        threading.Thread(
            target=self.search_worker,
            args=(query,),
            daemon=True
        ).start()

    def search_worker(self, query):

        try:

            search_query = (
                translate_query_to_english(
                    query
                )
            )

            params = urllib.parse.urlencode(
                {
                    "search":
                        search_query,

                    "page":
                        1
                }
            )

            url = (
                GUTENDEX_URL
                + "?"
                + params
            )

            data = get_json(
                url,
                timeout=45
            )

            books = data.get(
                "results",
                []
            )

            clean = []

            for book in books:

                # Public domain only
                if (
                    book.get(
                        "copyright"
                    ) is False

                    or

                    book.get(
                        "copyright"
                    ) is None
                ):

                    clean.append(
                        simple_book(book)
                    )

            Clock.schedule_once(
                lambda dt,
                b=clean:
                self.show_results(b)
            )

        except Exception as error:

            Clock.schedule_once(
                lambda dt,
                e=str(error):
                self.search_error(e)
            )

    def search_error(self, error):

        self.status.text = (
            self.tr("error")
        )

        show_popup(
            self.tr("error"),
            error
        )

    def show_results(self, books):

        self.results.clear_widgets()

        if not books:

            self.status.text = (
                self.tr("no_results")
            )

            return

        self.status.text = (
            str(len(books))
            + " "
            + self.tr("books_found")
        )

        for book in books:

            card = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(125),
                padding=dp(8),
                spacing=dp(4)
            )

            title = Label(
                text=ui_text(
                    book.get(
                        "title",
                        "Untitled"
                    ),
                    self.app.language
                ),
                bold=True,
                size_hint_y=None,
                height=dp(38),
                halign="center",
                valign="middle"
            )

            title.bind(
                size=lambda obj, value:
                setattr(
                    obj,
                    "text_size",
                    value
                )
            )

            author = Label(
                text=author_name(book),
                size_hint_y=None,
                height=dp(30)
            )

            button = Button(
                text=self.tr("open"),
                size_hint_y=None,
                height=dp(42)
            )

            button.bind(
                on_release=lambda x,
                b=book:
                self.open_book(b)
            )

            card.add_widget(title)
            card.add_widget(author)
            card.add_widget(button)

            self.results.add_widget(
                card
            )

    def open_book(self, book):

        try:

            self.app.details.load_book(
                book
            )

            self.app.sm.current = (
                "details"
            )

        except Exception as e:

            show_popup(
                self.tr("error"),
                str(e)
            )

    def open_library(self):

        self.app.library.refresh()

        self.app.sm.current = (
            "library"
        )

    def open_settings(self):

        self.app.sm.current = (
            "settings"
        )


# =========================================================
# DETAILS SCREEN
# =========================================================

class DetailsScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(
            name="details",
            **kwargs
        )

        self.app = App.get_running_app()

        self.book = None

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        top = BoxLayout(
            size_hint_y=None,
            height=dp(50)
        )

        self.back_button = Button(
            size_hint_x=None,
            width=dp(85)
        )

        self.back_button.bind(
            on_release=lambda x:
            self.go_back()
        )

        self.title_label = Label(
            bold=True
        )

        top.add_widget(
            self.back_button
        )

        top.add_widget(
            self.title_label
        )

        root.add_widget(top)

        scroll = ScrollView()

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            padding=dp(5)
        )

        content.bind(
            minimum_height=
            content.setter(
                "height"
            )
        )

        self.cover = Image(
            size_hint_y=None,
            height=dp(270)
        )

        content.add_widget(
            self.cover
        )

        self.info = Label(
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(160)
        )

        self.info.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        content.add_widget(
            self.info
        )

        buttons = GridLayout(
            cols=2,
            spacing=dp(5),
            size_hint_y=None,
            height=dp(220)
        )

        self.favorite_button = Button()
        self.download_button = Button()
        self.pdf_button = Button()
        self.translate_button = Button()

        self.favorite_button.bind(
            on_release=lambda x:
            self.toggle_favorite()
        )

        self.download_button.bind(
            on_release=lambda x:
            self.download_txt()
        )

        self.pdf_button.bind(
            on_release=lambda x:
            self.create_pdf()
        )

        self.translate_button.bind(
            on_release=lambda x:
            self.translate_to_persian()
        )

        buttons.add_widget(
            self.favorite_button
        )

        buttons.add_widget(
            self.download_button
        )

        buttons.add_widget(
            self.pdf_button
        )

        buttons.add_widget(
            self.translate_button
        )

        content.add_widget(
            buttons
        )

        self.preview = Label(
            halign="left",
            valign="top",
            size_hint_y=None
        )

        self.preview.bind(
            width=lambda obj, value:
            setattr(
                obj,
                "text_size",
                (value, None)
            )
        )

        self.preview.bind(
            texture_size=lambda obj, value:
            setattr(
                obj,
                "height",
                max(
                    dp(250),
                    value[1]
                )
            )
        )

        content.add_widget(
            self.preview
        )

        scroll.add_widget(
            content
        )

        root.add_widget(
            scroll
        )

        self.add_widget(root)

        self.update_language()

    def update_language(self):

        self.back_button.text = (
            self.app.tr("back")
        )

        self.favorite_button.text = (
            self.app.tr("favorite")
        )

        self.download_button.text = (
            self.app.tr("download_txt")
        )

        self.pdf_button.text = (
            self.app.tr("create_pdf")
        )

        self.translate_button.text = (
            self.app.tr("translate")
        )

    def go_back(self):

        self.app.sm.current = (
            "home"
        )

    def load_book(self, book):

        self.book = book

        self.app.storage.add_history(
            simple_book(book)
        )

        title = book.get(
            "title",
            "Untitled"
        )

        self.title_label.text = (
            ui_text(
                title,
                self.app.language
            )
        )

        languages = ", ".join(
            book.get(
                "languages",
                []
            )
        )

        info = (
            self.app.tr("author")
            + ": "
            + author_name(book)
            + "\n"
            + self.app.tr("language")
            + ": "
            + languages
            + "\n"
            + self.app.tr("downloads")
            + ": "
            + str(
                book.get(
                    "download_count",
                    0
                )
            )
            + "\n"
            + self.app.tr(
                "public_domain"
            )
            + ": Yes"
        )

        self.info.text = ui_text(
            info,
            self.app.language
        )

        self.preview.text = (
            self.app.tr(
                "book_ready"
            )
        )

        self.cover.source = ""

        url = cover_url(book)

        if url:

            threading.Thread(
                target=self.cover_worker,
                args=(url,),
                daemon=True
            ).start()

    def cover_worker(self, url):

        try:

            data = http_get(
                url,
                timeout=30
            )

            folder = os.path.join(
                self.app.user_data_dir,
                "covers"
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            path = os.path.join(
                folder,
                str(
                    self.book.get(
                        "id",
                        "cover"
                    )
                )
                + ".jpg"
            )

            with open(
                path,
                "wb"
            ) as f:

                f.write(data)

            Clock.schedule_once(
                lambda dt,
                p=path:
                self.set_cover(p)
            )

        except Exception as e:

            print(
                "COVER ERROR:",
                e
            )

    def set_cover(self, path):

        try:

            self.cover.source = path

            self.cover.reload()

        except Exception:
            pass

    def toggle_favorite(self):

        if not self.book:
            return

        result = (
            self.app.storage.toggle_favorite(
                simple_book(
                    self.book
                )
            )
        )

        if result:

            show_popup(
                self.app.tr(
                    "favorite"
                ),
                self.app.tr(
                    "saved"
                )
            )

    # =====================================================
    # DOWNLOAD TXT
    # =====================================================

    def download_txt(self):

        if not self.book:
            return

        url = text_url(
            self.book
        )

        if not url:

            show_popup(
                self.app.tr("error"),
                "TXT source is not available."
            )

            return

        threading.Thread(
            target=self.download_worker,
            args=(url,),
            daemon=True
        ).start()

    def download_worker(self, url):

        try:

            data = http_get(
                url,
                timeout=120
            )

            title = safe_filename(
                self.book.get(
                    "title",
                    "book"
                )
            )

            path = os.path.join(
                self.app.download_folder,
                title + ".txt"
            )

            with open(
                path,
                "wb"
            ) as f:

                f.write(data)

            show_popup(
                self.app.tr(
                    "download_complete"
                ),
                path
            )

        except Exception as error:

            show_popup(
                self.app.tr("error"),
                str(error)
            )

    # =====================================================
    # PDF
    # =====================================================

    def create_pdf(self):

        if not REPORTLAB_OK:

            show_popup(
                "PDF",
                "ReportLab is not installed.\n\n"
                "Install:\n"
                "pip install reportlab"
            )

            return

        if not self.book:
            return

        url = text_url(
            self.book
        )

        if not url:

            show_popup(
                "PDF",
                "TXT source is not available."
            )

            return

        threading.Thread(
            target=self.pdf_worker,
            args=(url,),
            daemon=True
        ).start()

    def pdf_worker(self, url):

        try:

            data = http_get(
                url,
                timeout=120
            )

            text = clean_gutenberg(
                data.decode(
                    "utf-8",
                    errors="replace"
                )
            )

            title = self.book.get(
                "title",
                "Book"
            )

            path = os.path.join(
                self.app.download_folder,
                safe_filename(title)
                + ".pdf"
            )

            create_pdf(
                text,
                title,
                path
            )

            show_popup(
                "PDF",
                path
            )

        except Exception as error:

            show_popup(
                "PDF Error",
                str(error)
            )

    # =====================================================
    # TRANSLATION
    # =====================================================

    def translate_to_persian(self):

        if not self.book:
            return

        url = text_url(
            self.book
        )

        if not url:

            show_popup(
                self.app.tr("error"),
                "TXT source is not available."
            )

            return

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        progress = Label(
            text=rtl_text(
                self.app.tr(
                    "translation_start"
                )
            )
        )

        root.add_widget(
            progress
        )

        popup = Popup(
            title=self.app.tr(
                "translation"
            ),
            content=root,
            size_hint=(0.9, 0.35),
            auto_dismiss=False
        )

        popup.open()

        threading.Thread(
            target=self.translation_worker,
            args=(
                url,
                popup,
                progress
            ),
            daemon=True
        ).start()

    def translation_worker(
        self,
        url,
        popup,
        progress
    ):

        try:

            data = http_get(
                url,
                timeout=120
            )

            original = clean_gutenberg(
                data.decode(
                    "utf-8",
                    errors="replace"
                )
            )

            if not original.strip():

                raise Exception(
                    "The book has no readable text."
                )

            translated = (
                translate_book_to_persian(
                    original,
                    progress
                )
            )

            title = safe_filename(
                self.book.get(
                    "title",
                    "book"
                )
            )

            txt_path = os.path.join(
                self.app.download_folder,
                title
                + "_Persian.txt"
            )

            with open(
                txt_path,
                "w",
                encoding="utf-8-sig"
            ) as f:

                f.write(
                    translated
                )

            pdf_path = ""

            if REPORTLAB_OK:

                try:

                    pdf_path = os.path.join(
                        self.app.download_folder,
                        title
                        + "_Persian.pdf"
                    )

                    create_pdf(
                        translated,
                        title
                        + " - ترجمه فارسی",
                        pdf_path
                    )

                except Exception as e:

                    print(
                        "PERSIAN PDF ERROR:",
                        e
                    )

                    pdf_path = ""

            record = {

                "id":
                    self.book.get("id"),

                "title":
                    self.book.get(
                        "title",
                        "Untitled"
                    ),

                "language":
                    "Persian",

                "code":
                    "fa",

                "txt_path":
                    txt_path,

                "pdf_path":
                    pdf_path,
            }

            self.app.storage.data[
                "translated"
            ] = [

                x for x in
                self.app.storage.data[
                    "translated"
                ]

                if x.get("id")
                != record.get("id")
            ]

            self.app.storage.data[
                "translated"
            ].insert(
                0,
                record
            )

            self.app.storage.save()

            def finish(_dt):

                try:
                    popup.dismiss()
                except Exception:
                    pass

                self.preview.text = (
                    rtl_text(
                        translated[:12000]
                    )
                )

                message = (
                    self.app.tr(
                        "translation_complete"
                    )
                    + "\n\nTXT:\n"
                    + txt_path
                )

                if pdf_path:

                    message += (
                        "\n\nPDF:\n"
                        + pdf_path
                    )

                show_popup(
                    self.app.tr(
                        "translation_complete"
                    ),
                    message
                )

            Clock.schedule_once(
                finish
            )

        except Exception as error:

            def failed(_dt):

                try:
                    popup.dismiss()
                except Exception:
                    pass

                show_popup(
                    self.app.tr(
                        "translation_failed"
                    ),
                    str(error)
                )

            Clock.schedule_once(
                failed
            )


# =========================================================
# GUTENBERG CLEANER
# =========================================================

def clean_gutenberg(text):

    text = str(text)

    starts = [

        "*** START OF THE PROJECT GUTENBERG",

        "*** START OF THIS PROJECT GUTENBERG",
    ]

    ends = [

        "*** END OF THE PROJECT GUTENBERG",

        "*** END OF THIS PROJECT GUTENBERG",
    ]

    for marker in starts:

        if marker in text:

            text = text.split(
                marker,
                1
            )[1]

            break

    for marker in ends:

        if marker in text:

            text = text.split(
                marker,
                1
            )[0]

            break

    return text.strip()


# =========================================================
# GOOGLE TRANSLATE
# =========================================================

def google_translate(
    text,
    target="fa"
):

    encoded = urllib.parse.quote(
        text
    )

    url = (
        "https://translate.googleapis.com/"
        "translate_a/single"
        "?client=gtx"
        "&sl=auto"
        "&tl="
        + target
        + "&dt=t"
        "&q="
        + encoded
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0 "
                "(Android; NaimiBook/7.0)"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=70
    ) as response:

        raw = response.read()

    data = json.loads(
        raw.decode(
            "utf-8",
            errors="replace"
        )
    )

    result = []

    for item in data[0]:

        if item and item[0]:

            result.append(
                item[0]
            )

    return "".join(
        result
    )


# =========================================================
# TRANSLATION CHUNKS
# =========================================================

def make_chunks(
    text,
    maximum=3000
):

    paragraphs = text.splitlines()

    chunks = []

    current = ""

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        if len(paragraph) > maximum:

            if current:

                chunks.append(
                    current
                )

                current = ""

            words = paragraph.split()

            part = ""

            for word in words:

                candidate = (
                    word
                    if not part
                    else part + " " + word
                )

                if len(candidate) <= maximum:

                    part = candidate

                else:

                    if part:
                        chunks.append(
                            part
                        )

                    part = word

            if part:
                chunks.append(
                    part
                )

            continue

        candidate = (
            paragraph
            if not current
            else current
            + "\n"
            + paragraph
        )

        if len(candidate) <= maximum:

            current = candidate

        else:

            if current:

                chunks.append(
                    current
                )

            current = paragraph

    if current:

        chunks.append(
            current
        )

    return chunks


def translate_chunk(chunk):

    waits = [
        5,
        10,
        20,
        40
    ]

    last_error = None

    for attempt in range(4):

        try:

            result = google_translate(
                chunk,
                "fa"
            )

            if result:

                return result

            raise Exception(
                "Empty translation response."
            )

        except Exception as error:

            last_error = error

            msg = str(error).lower()

            if (
                "429" in msg
                or
                "too many requests"
                in msg
            ):

                time.sleep(
                    waits[
                        min(
                            attempt,
                            len(waits) - 1
                        )
                    ]
                )

                continue

            if (
                "timeout" in msg
                or
                "connection" in msg
            ):

                time.sleep(
                    5 * (attempt + 1)
                )

                continue

            raise

    raise Exception(
        "Translation service is temporarily unavailable."
    )


def translate_book_to_persian(
    text,
    progress=None
):

    chunks = make_chunks(
        text,
        3000
    )

    total = len(chunks)

    if total == 0:
        return ""

    result = []

    for index, chunk in enumerate(
        chunks
    ):

        percent = int(
            (index / total)
            * 100
        )

        if progress:

            Clock.schedule_once(
                lambda dt,
                n=index + 1,
                t=total,
                p=percent:
                setattr(
                    progress,
                    "text",
                    rtl_text(
                        "ترجمه بخش "
                        + str(n)
                        + " از "
                        + str(t)
                        + " - "
                        + str(p)
                        + "%"
                    )
                )
            )

        result.append(
            translate_chunk(chunk)
        )

        if index < total - 1:

            time.sleep(3)

    if progress:

        Clock.schedule_once(
            lambda dt:
            setattr(
                progress,
                "text",
                rtl_text(
                    "ترجمه کامل شد، در حال ذخیره..."
                )
            )
        )

    return "\n\n".join(
        result
    )


# =========================================================
# PDF FONT
# =========================================================

def register_pdf_font():

    global PDF_FONT_NAME

    if not REPORTLAB_OK:
        return None

    if not ARABIC_FONT:
        return None

    if PDF_FONT_NAME:
        return PDF_FONT_NAME

    try:

        PDF_FONT_NAME = "NaimiArabic"

        pdfmetrics.registerFont(
            TTFont(
                PDF_FONT_NAME,
                ARABIC_FONT
            )
        )

        return PDF_FONT_NAME

    except Exception as e:

        print(
            "PDF FONT ERROR:",
            e
        )

        PDF_FONT_NAME = None

        return None


# =========================================================
# PDF RTL
# =========================================================

def shape_pdf(text):

    text = str(text)

    if not has_persian(text):
        return text

    if not RTL_OK:

        raise Exception(
            "arabic_reshaper and python-bidi are required "
            "for Persian PDF."
        )

    try:

        reshaped = (
            arabic_reshaper.reshape(
                text
            )
        )

        return get_display(
            reshaped
        )

    except Exception as e:

        raise Exception(
            "Persian text shaping failed: "
            + str(e)
        )


def wrap_text(
    text,
    limit=80
):

    lines = []

    for paragraph in text.splitlines():

        paragraph = paragraph.strip()

        if not paragraph:

            lines.append("")

            continue

        words = paragraph.split()

        current = ""

        for word in words:

            candidate = (
                word
                if not current
                else current
                + " "
                + word
            )

            if len(candidate) <= limit:

                current = candidate

            else:

                if current:

                    lines.append(
                        current
                    )

                current = word

        if current:

            lines.append(
                current
            )

    return lines


# =========================================================
# CREATE PDF
# =========================================================

def create_pdf(
    text,
    title,
    path
):

    if not REPORTLAB_OK:

        raise Exception(
            "ReportLab is not installed."
        )

    persian = (
        has_persian(text)
        or
        has_persian(title)
    )

    font = None

    if persian:

        font = register_pdf_font()

        if not font:

            raise Exception(
                "Persian font not found.\n\n"
                "Put NotoNaskhArabic-Regular.ttf "
                "next to main.py."
            )

    pdf = canvas.Canvas(
        path,
        pagesize=A4
    )

    width, height = A4

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    if persian:

        pdf.setFont(
            font,
            16
        )

        pdf.drawCentredString(
            width / 2,
            height - 45,
            shape_pdf(title)
        )

    else:

        pdf.setFont(
            "Helvetica-Bold",
            16
        )

        pdf.drawCentredString(
            width / 2,
            height - 45,
            title
        )

    y = height - 80

    # -----------------------------------------------------
    # BODY
    # -----------------------------------------------------

    for line in wrap_text(text):

        if y < 45:

            pdf.showPage()

            y = height - 45

        if not line:

            y -= 12

            continue

        if has_persian(line):

            pdf.setFont(
                font,
                11
            )

            pdf.drawRightString(
                width - 45,
                y,
                shape_pdf(line)
            )

        else:

            pdf.setFont(
                "Helvetica",
                10
            )

            pdf.drawString(
                45,
                y,
                line
            )

        y -= 15

    pdf.save()


# =========================================================
# LIBRARY SCREEN
# =========================================================

class LibraryScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(
            name="library",
            **kwargs
        )

        self.app = App.get_running_app()

        self.current = "history"

        root = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        top = BoxLayout(
            size_hint_y=None,
            height=dp(50)
        )

        self.back = Button(
            size_hint_x=None,
            width=dp(85)
        )

        self.back.bind(
            on_release=lambda x:
            self.go_back()
        )

        self.title = Label(
            bold=True
        )

        top.add_widget(
            self.back
        )

        top.add_widget(
            self.title
        )

        root.add_widget(top)

        tabs = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(4)
        )

        self.history_btn = Button()
        self.favorite_btn = Button()
        self.translated_btn = Button()

        self.history_btn.bind(
            on_release=lambda x:
            self.show("history")
        )

        self.favorite_btn.bind(
            on_release=lambda x:
            self.show("favorites")
        )

        self.translated_btn.bind(
            on_release=lambda x:
            self.show("translated")
        )

        tabs.add_widget(
            self.history_btn
        )

        tabs.add_widget(
            self.favorite_btn
        )

        tabs.add_widget(
            self.translated_btn
        )

        root.add_widget(tabs)

        self.clear_btn = Button(
            size_hint_y=None,
            height=dp(45)
        )

        self.clear_btn.bind(
            on_release=lambda x:
            self.clear_current()
        )

        root.add_widget(
            self.clear_btn
        )

        scroll = ScrollView()

        self.box = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None
        )

        self.box.bind(
            minimum_height=
            self.box.setter(
                "height"
            )
        )

        scroll.add_widget(
            self.box
        )

        root.add_widget(
            scroll
        )

        self.add_widget(root)

        self.update_language()

    def update_language(self):

        self.back.text = (
            self.app.tr("back")
        )

        self.title.text = (
            self.app.tr("library")
        )

        self.history_btn.text = (
            self.app.tr("history")
        )

        self.favorite_btn.text = (
            self.app.tr("favorites")
        )

        self.translated_btn.text = (
            self.app.tr("translated")
        )

        self.clear_btn.text = (
            self.app.tr("clear")
        )

    def go_back(self):

        self.app.sm.current = (
            "home"
        )

    def refresh(self):

        self.show(
            self.current
        )

    def show(self, section):

        self.current = section

        self.box.clear_widgets()

        items = self.app.storage.data.get(
            section,
            []
        )

        if not items:

            if section == "history":
                key = "history_empty"

            elif section == "favorites":
                key = "favorites_empty"

            else:
                key = "translated_empty"

            self.box.add_widget(
                Label(
                    text=rtl_text(
                        self.app.tr(key)
                    ),
                    size_hint_y=None,
                    height=dp(70)
                )
            )

            return

        for item in items:

            if section == "translated":

                self.add_translation(
                    item
                )

            else:

                self.add_book(
                    item
                )

    def add_book(self, book):

        row = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(110),
            spacing=dp(4)
        )

        row.add_widget(
            Label(
                text=ui_text(
                    book.get(
                        "title",
                        "Untitled"
                    ),
                    self.app.language
                ),
                bold=True
            )
        )

        row.add_widget(
            Label(
                text=author_name(book)
            )
        )

        btn = Button(
            text=self.app.tr("open"),
            size_hint_y=None,
            height=dp(40)
        )

        btn.bind(
            on_release=lambda x,
            b=book:
            self.open_book(b)
        )

        row.add_widget(btn)

        self.box.add_widget(
            row
        )

    def add_translation(self, item):

        row = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            spacing=dp(4)
        )

        row.add_widget(
            Label(
                text=ui_text(
                    item.get(
                        "title",
                        "Untitled"
                    ),
                    self.app.language
                ),
                bold=True
            )
        )

        row.add_widget(
            Label(
                text=rtl_text("فارسی")
            )
        )

        txt = item.get(
            "txt_path",
            ""
        )

        txt_btn = Button(
            text=self.app.tr(
                "open_txt"
            ),
            size_hint_y=None,
            height=dp(40)
        )

        txt_btn.bind(
            on_release=lambda x,
            p=txt:
            open_file(p)
        )

        row.add_widget(
            txt_btn
        )

        pdf = item.get(
            "pdf_path",
            ""
        )

        if pdf:

            pdf_btn = Button(
                text=self.app.tr(
                    "open_pdf"
                ),
                size_hint_y=None,
                height=dp(40)
            )

            pdf_btn.bind(
                on_release=lambda x,
                p=pdf:
                open_file(p)
            )

            row.add_widget(
                pdf_btn
            )

        self.box.add_widget(
            row
        )

    def open_book(self, book):

        self.app.details.load_book(
            book
        )

        self.app.sm.current = (
            "details"
        )

    def clear_current(self):

        self.app.storage.data[
            self.current
        ] = []

        self.app.storage.save()

        self.show(
            self.current
        )


# =========================================================
# OPEN FILE
# =========================================================

def open_file(path):

    if not path:

        show_popup(
            "File",
            "File path is empty."
        )

        return

    if not os.path.isfile(path):

        show_popup(
            "File",
            "File not found:\n"
            + path
        )

        return

    try:

        subprocess.Popen(
            [
                "am",
                "start",
                "-a",
                "android.intent.action.VIEW",
                "-d",
                "file://"
                + path
            ]
        )

    except Exception as error:

        show_popup(
            "File",
            str(error)
        )


# =========================================================
# SETTINGS SCREEN
# =========================================================

class SettingsScreen(Screen):

    def __init__(self, **kwargs):

        super().__init__(
            name="settings",
            **kwargs
        )

        self.app = App.get_running_app()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        top = BoxLayout(
            size_hint_y=None,
            height=dp(50)
        )

        self.back = Button(
            size_hint_x=None,
            width=dp(85)
        )

        self.back.bind(
            on_release=lambda x:
            self.go_back()
        )

        self.title = Label(
            bold=True
        )

        top.add_widget(
            self.back
        )

        top.add_widget(
            self.title
        )

        root.add_widget(top)

        self.language_label = Label(
            size_hint_y=None,
            height=dp(40)
        )

        root.add_widget(
            self.language_label
        )

        self.language_spinner = Spinner(
            text="فارسی",
            values=[
                "فارسی",
                "English"
            ],
            size_hint_y=None,
            height=dp(50)
        )

        self.language_spinner.bind(
            text=self.change_language
        )

        root.add_widget(
            self.language_spinner
        )

        self.folder_btn = Button(
            size_hint_y=None,
            height=dp(50)
        )

        self.folder_btn.bind(
            on_release=lambda x:
            show_popup(
                self.app.tr(
                    "download_folder"
                ),
                self.app.download_folder
            )
        )

        root.add_widget(
            self.folder_btn
        )

        self.pdf_btn = Button(
            size_hint_y=None,
            height=dp(50)
        )

        self.pdf_btn.bind(
            on_release=lambda x:
            self.pdf_status()
        )

        root.add_widget(
            self.pdf_btn
        )

        self.about_btn = Button(
            size_hint_y=None,
            height=dp(50)
        )

        self.about_btn.bind(
            on_release=lambda x:
            show_popup(
                self.app.tr("about"),
                "Naimi Book\n\n"
                "Public-domain book library."
            )
        )

        root.add_widget(
            self.about_btn
        )

        self.add_widget(root)

        self.update_language()

    def update_language(self):

        self.back.text = (
            self.app.tr("back")
        )

        self.title.text = (
            self.app.tr("settings")
        )

        self.language_label.text = (
            self.app.tr(
                "language_setting"
            )
        )

        self.folder_btn.text = (
            self.app.tr(
                "download_folder"
            )
        )

        self.pdf_btn.text = (
            self.app.tr(
                "pdf_support"
            )
        )

        self.about_btn.text = (
            self.app.tr("about")
        )

        self.language_spinner.text = (
            "فارسی"
            if self.app.language == "fa"
            else "English"
        )

    def change_language(
        self,
        spinner,
        value
    ):

        if value == "فارسی":

            self.app.set_language(
                "fa"
            )

        else:

            self.app.set_language(
                "en"
            )

    def pdf_status(self):

        status = (

            "ReportLab: "
            + (
                "OK"
                if REPORTLAB_OK
                else "Not installed"
            )

            + "\n\n"

            "RTL support: "
            + (
                "OK"
                if RTL_OK
                else "Not installed"
            )

            + "\n\n"

            "Persian font: "
            + (
                "Found"
                if ARABIC_FONT
                else "Not found"
            )
        )

        show_popup(
            self.app.tr(
                "pdf_support"
            ),
            status
        )

    def go_back(self):

        self.app.sm.current = (
            "home"
        )


# =========================================================
# APP
# =========================================================

class NaimiBook(App):

    def build(self):

        self.title = "Naimi Book"

        self.language = "fa"

        self.download_folder = (
            get_download_folder()
        )

        self.storage = Storage()

        self.sm = ScreenManager(
            transition=NoTransition()
        )

        self.home = HomeScreen()

        self.details = DetailsScreen()

        self.library = LibraryScreen()

        self.settings = SettingsScreen()

        self.sm.add_widget(
            self.home
        )

        self.sm.add_widget(
            self.details
        )

        self.sm.add_widget(
            self.library
        )

        self.sm.add_widget(
            self.settings
        )

        return self.sm

    def tr(self, key):

        return UI.get(
            self.language,
            UI["en"]
        ).get(
            key,
            key
        )

    def set_language(
        self,
        language
    ):

        self.language = language

        self.home.update_language()

        self.details.update_language()

        self.library.update_language()

        self.settings.update_language()

        if language == "fa":

            self.title = "کتابخانه نعیمی"

        else:

            self.title = "NAIMI BOOK"

        self.sm.current = "home"


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    try:

        NaimiBook().run()

    except Exception as error:

        print(
            "================================"
        )

        print(
            "NAIMI BOOK ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "================================"
        )