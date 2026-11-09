#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PILATES ONE STEP 静的サイト生成スクリプト

共通パーツ（ヘッダー・フッター・CTA・構造化データ）をまとめて管理し、
site/ 以下に各ページの index.html を書き出します。

    python3 _build/build.py
"""
import html
import re
import json
import os
import struct
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
IMG_DIR = os.path.join(OUT, "assets", "img")

SITE = "https://onestep-p.jp"
BRAND = "PILATES ONE STEP"
TRIAL = "https://pilates-onestep.hacomono.jp/reserve?trial=true&from=home"
MEMBER = "https://pilates-onestep.hacomono.jp/reserve?from=home"
REGISTER = "https://pilates-onestep.hacomono.jp/register/"
INSTAGRAM = "https://www.instagram.com/pilates_one_step/"
LINE = "https://lin.ee/NUrgw2g"
UPDATED = "2026-10-31"

# トップの料金カードの数字・見出し用（太い丸ゴシック）
HAND_FONT = '\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Yomogi&display=swap">'  # 体験の流れの手書きバッジ用
PRICE_FONT = '\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@700;900&display=swap">'

# CSS・JSの内容が変わると値も変わり、ブラウザに古いファイルが残らないようにする
def _asset_ver():
    import hashlib
    h = hashlib.md5()
    for f in ("assets/css/style.css", "assets/js/main.js"):
        with open(os.path.join(OUT, f), "rb") as fp:
            h.update(fp.read())
    return h.hexdigest()[:8]


ASSET_VER = _asset_ver()

NAV = [
    ("/", "トップ", "TOP"),
    ("/about/", "私たちについて", "ABOUT"),
    ("/news/", "お知らせ", "NEWS"),
    ("/price/", "料金", "PRICE"),
    ("/flow/", "体験の流れ", "FLOW"),
    ("/faq/", "よくある質問", "FAQ"),
    ("/contact/", "お問い合わせ", "CONTACT"),
]

STORES = [
    {
        "key": "hirao", "name": "平尾店", "en": "HIRAO",
        "zip": "810-0015", "region": "福岡県", "locality": "福岡市中央区",
        "street": "那の川2-9-32 ブルク平尾2F",
        "area": "平尾・薬院・高宮エリア",
        "areas": ["平尾", "薬院", "高宮", "那の川"],
        "img": "studio-hirao.jpg",
        "desc": "ミントカラーの壁と木のぬくもりが心地よい、明るく落ち着いたスタジオ。平尾・薬院・高宮エリアからも通いやすい立地です。",
    },
    {
        "key": "akasaka", "name": "赤坂店", "en": "AKASAKA",
        "zip": "810-0042", "region": "福岡県", "locality": "福岡市中央区",
        "street": "赤坂3-11-41 ルネッサンス21赤坂けやき通り 2F",
        "area": "赤坂・警固エリア",
        "areas": ["赤坂", "警固", "けやき通り"],
        "img": "studio-akasaka.jpg",
        "desc": "けやき通りエリアにある、大きな窓から光が差し込む開放的なスタジオ。赤坂・警固エリアからも通いやすい立地です。",
    },
]


def addr(s):
    return f"{s['region']}{s['locality']}{s['street']}"


def map_url(s):
    return "https://www.google.com/maps/search/?api=1&query=" + quote(f"{addr(s)} {BRAND}")


# ---------------------------------------------------------------- utilities
def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- photos
SRC_IMG = os.path.join(ROOT, "image")
BUILD_DIR = os.path.dirname(os.path.abspath(__file__))
# サイト用ファイル名: (image/ の元ファイル名, 長辺の最大px)
PHOTOS = {
    "hero-studio-class": ("back05.jpg", 2000),
    "about-hero": ("AI_IMG_0848k1.png", 1264),
    "price-hero": ("AI_IMG_3165k1.png", 1200),
    "flow-hero": ("IMG_9144.jpg", 1800),
    "faq-hero": ("AI_IMG_3165k3.png", 1200),
    "contact-hero": ("AI_IMG_0030k.png", 1264),
    "news-hero": ("IMG_2182.jpg", 1800),
    "cta-woman": ("S__141770801.jpg", 1200),
    "private-lesson": ("S__141770802.jpg", 1000),
    "studio-hirao": ("IMG_3165kk.jpg", 1200),
    "studio-akasaka": ("IMG_0848kk.png", 1200),
    "logo-sign": ("IMG_3159.jpg", 1200),
    "instructor-ring-support": ("IMG_0087.jpg", 1000),
    "cadillac-arm-support": ("IMG_0321.jpg", 1000),
    "beginner-support": ("IMG_0495.jpg", 1000),
    "reformer-side-stretch": ("IMG_2183.jpg", 1000),
    "ring-kneeling-group": ("IMG_2184.jpg", 1000),
    "feature-50min": ("AI_IMG_8831.png", 1000),
    "lesson-basic": ("IMG_8471.jpg", 1000),
    "lesson-posture": ("AI_IMG_8471k2.png", 1000),
    "about-group": ("IMG_8425.jpg", 1000),
    "about-refresh": ("AI_IMG_3165k1.png", 1000),
    "lesson-legs": ("AI_IMG_8831k1.png", 1000),
    "price-trial": ("AI_IMG_3165k4.png", 1000),
    "flow-consult": ("AI_IMG_0087k.png", 1000),
    "flow-reserve-phone": ("35261117_mk.jpg", 911),
    "flow-reserve-screen": ("25088755_mk.jpg", 1000),
    "ring-kneeling-class": ("IMG_2186.jpg", 1000),
    "reformer-leg-strap": ("IMG_2187.jpg", 1000),
    "ring-smile": ("IMG_2190.jpg", 1000),
    "instructor-check": ("IMG_2191.jpg", 1000),
    "cadillac-roll": ("IMG_2194.jpg", 1000),
    "instructor-arm-strap": ("IMG_2195.jpg", 1000),
    "reformer-posture": ("IMG_8429.jpg", 1000),
    "side-stretch-closeup": ("IMG_8471.jpg", 1000),
    "ring-teal-wall": ("IMG_8582.jpg", 1000),
    "small-group-ring": ("IMG_8601.jpg", 1000),
    "ring-group-row": ("IMG_8608.jpg", 1000),
    "ring-group-arms": ("IMG_8609.jpg", 1000),
    "ring-reformer-group": ("IMG_8616 2.jpg", 1000),
    "leg-strap-reformer": ("IMG_8831.jpg", 1000),
    "core-reformer-class": ("IMG_9075.jpg", 1000),
}
JPEG_QUALITY = 0.65
# ファビコン: (ファイル名, サイズpx, ロゴまわりの余白率, 角丸率)。iPhone用は端末側で角丸になるので四角のまま
FAVICONS = [
    ("favicon-32.png", 32, 0.14, 0.22),
    ("favicon-192.png", 192, 0.16, 0.22),
    ("apple-touch-icon.png", 180, 0.18, 0),
]
FAVICON_LINKS = ('<link rel="icon" href="/assets/img/favicon-32.png" sizes="32x32" type="image/png">'
                 '<link rel="icon" href="/assets/img/favicon-192.png" sizes="192x192" type="image/png">'
                 '<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">')
# Googleのタグ（現サイトと同じGTM・GA4）。確認用の preview/ からは build_preview() で取り除く
GTM_ID = "GTM-KJQLTH5S"
GA_ID = "G-X0ECD1JVMX"
GTM_HEAD = f"""<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM_ID}');</script>
<!-- End Google Tag Manager -->"""
GTAG = f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA_ID}');
</script>
<!-- End Google tag (gtag.js) -->"""
GTM_BODY = f"""<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""
# 人物を切り抜いて使う写真: サイト用ファイル名: (image/ の元ファイル名, 横幅px)
CUTOUTS = {
    "private-cutout": ("IMG_0495-.png", 520),
}


def swift_tool(name):
    """_build/ のSwiftツールを初回だけコンパイルする（macOS標準の画像処理を使用）"""
    import subprocess
    src = os.path.join(BUILD_DIR, name + ".swift")
    exe = os.path.join(BUILD_DIR, ".bin", name)
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        os.makedirs(os.path.dirname(exe), exist_ok=True)
        print(f"compiling {name} ...")
        subprocess.run(["swiftc", "-O", src, "-o", exe], check=True, stderr=subprocess.DEVNULL)
    return exe


def converter():
    return swift_tool("convert_image")


PHOTO_CACHE = os.path.join(BUILD_DIR, ".cache", "photos.json")


def build_photos():
    """image/ の素材のうち、前回の変換から変わったものだけを site/assets/img/ に書き出す

    「元ファイルの大きさ・更新日時・変換設定」を記録しておき、どれか1つでも変わったら変換し直す。
    （日時が新しいかどうかでは判定しないので、古い日時のままコピーした写真でも差し替わる）
    """
    import shutil
    import subprocess
    try:
        with open(PHOTO_CACHE, encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        cache = {}
    done = 0

    def run(dest, src, setting, make):
        nonlocal done
        st = os.stat(src)
        sig = [st.st_size, int(st.st_mtime), setting]
        if os.path.exists(dest) and cache.get(os.path.basename(dest)) == sig:
            return
        make()
        cache[os.path.basename(dest)] = sig
        done += 1

    for name, (src, size) in PHOTOS.items():
        s, d = os.path.join(SRC_IMG, src), os.path.join(IMG_DIR, name + ".jpg")
        run(d, s, [src, size, JPEG_QUALITY],
            lambda s=s, d=d, size=size: subprocess.run([converter(), s, d, str(size), str(JPEG_QUALITY)], check=True))
    # 人物の切り抜き（背景透過PNG）：macOS標準の人物認識で背景を取り除く
    for name, (src, width) in CUTOUTS.items():
        s, d = os.path.join(SRC_IMG, src), os.path.join(IMG_DIR, name + ".png")
        run(d, s, [src, width], lambda s=s, d=d, width=width: subprocess.run(
            [swift_tool("cutout_person"), s, d, str(width)], check=True, stdout=subprocess.DEVNULL))
    # ファビコン：白いダイヤ（250730_favicon_thick_white.png）をミント色の角丸にのせる
    fav_src = os.path.join(SRC_IMG, "250730_favicon_thick_white.png")
    for name, size, pad, radius in FAVICONS:
        d = os.path.join(IMG_DIR, name)
        run(d, fav_src, [size, pad, radius], lambda d=d, size=size, pad=pad, radius=radius: subprocess.run(
            [swift_tool("make_icon"), fav_src, d, str(size), str(pad), "4fbdb5", str(radius)], check=True))

    # キャッチのSVG：Illustratorの黒(#231815)をサイトの紺色に置き換えて書き出す
    def write_catch():
        svg = open(os.path.join(SRC_IMG, "catch01.svg"), encoding="utf-8").read().replace("#231815", "#1d3a4a")
        with open(os.path.join(IMG_DIR, "catch01.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    run(os.path.join(IMG_DIR, "catch01.svg"), os.path.join(SRC_IMG, "catch01.svg"), "navy", write_catch)
    # aboutの「こんな方におすすめ」のイラスト：4枚の縮尺をそろえるため、全部同じ倍率（50%）で縮小
    for i in range(1, 5):
        name = f"about0{i}.png"
        d, src = os.path.join(IMG_DIR, name), os.path.join(SRC_IMG, name)
        w, h = png_size(src)
        run(d, src, "png50", lambda d=d, src=src, w=w, h=h: subprocess.run(
            ["sips", "-z", str(h // 2), str(w // 2), src, "--out", d], check=True, capture_output=True))

    # Illustratorで作成した手書き風SVG（色はそのまま使う）
    for name in ("subcatch.svg", "subcatch01.svg", "fight.svg", "try.svg", "check.svg", "welove.svg"):
        run(os.path.join(IMG_DIR, name), os.path.join(SRC_IMG, name), "copy",
            lambda name=name: shutil.copy2(os.path.join(SRC_IMG, name), os.path.join(IMG_DIR, name)))
    run(os.path.join(IMG_DIR, "logo.png"), os.path.join(SRC_IMG, "logo.png"), "copy",
        lambda: shutil.copy2(os.path.join(SRC_IMG, "logo.png"), os.path.join(IMG_DIR, "logo.png")))

    os.makedirs(os.path.dirname(PHOTO_CACHE), exist_ok=True)
    with open(PHOTO_CACHE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    print(f"photos: {done} updated")


def png_size(path):
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])


def jpeg_size(path):
    with open(path, "rb") as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return None


_sizes = {}


_vers = {}


def img_url(src):
    """/assets/img/ の画像URL。中身が変わると ?v= の値も変わり、ブラウザが新しい画像を読み直す"""
    if src not in _vers:
        import hashlib
        with open(os.path.join(IMG_DIR, src), "rb") as f:
            _vers[src] = hashlib.md5(f.read()).hexdigest()[:8]
    return f"/assets/img/{src}?v={_vers[src]}"


def img(src, alt, cls="", eager=False, sizes=None):
    if src not in _sizes:
        path = os.path.join(IMG_DIR, src)
        _sizes[src] = png_size(path) if src.endswith(".png") else jpeg_size(path)
    w, h = _sizes[src]
    attrs = [f'src="{img_url(src)}"', f'alt="{esc(alt)}"', f'width="{w}"', f'height="{h}"']
    if cls:
        attrs.append(f'class="{cls}"')
    attrs.append('fetchpriority="high"' if eager else 'loading="lazy"')
    attrs.append('decoding="async"')
    return "<img " + " ".join(attrs) + ">"


ICONS = {
    "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    "chev": '<path d="m9 6 6 6-6 6"/>',
    "chevdown": '<path d="m6 9 6 6 6-6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "woman": '<path d="M8.2 13.2C6.6 11.6 6.9 7.6 8 6 9.1 4.2 10.6 3.6 12.3 3.6c2.6 0 4.6 1.9 4.6 5 0 1.6-.2 3.3.9 4.8"/><path d="M9 7.3c1.6.3 3.6-.6 4.6-2.2.5 1.4 1.6 2.4 2.7 2.8"/><path d="M9 8.4c0 2.3 1.4 4.3 3.1 4.3s3.1-2 3.1-4.3"/><path d="M5.2 21c.4-3 2.6-5.3 5.2-5.8l1.6 1.6 1.6-1.6c2.6.5 4.8 2.8 5.2 5.8"/>',
    "users": '<circle cx="12" cy="8" r="3.4"/><path d="M5.8 20.5c0-3.6 2.7-6.1 6.2-6.1s6.2 2.5 6.2 6.1"/><path d="M6.3 11.9a2.6 2.6 0 1 1 .9-5"/><path d="M1.5 18.5c0-2.8 1.8-4.8 4.2-5.1"/><path d="M17.7 11.9a2.6 2.6 0 1 0-.9-5"/><path d="M22.5 18.5c0-2.8-1.8-4.8-4.2-5.1"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 6.5V12l3.5 2"/>',
    "sprout": '<path d="M12 21v-9"/><path d="M12 12C12 7.5 8.5 5 4 5c0 4.5 3.5 7 8 7z"/><path d="M12 10c0-4 3-6.5 8-6.5 0 4-3 6.5-8 6.5z"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "calendar": '<rect x="3" y="4.5" width="18" height="17" rx="2"/><path d="M16 2.5v4M8 2.5v4M3 10h18"/><path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
    "store": '<path d="M3 9.5 4.5 4h15L21 9.5"/><path d="M4.5 10.5V20h15v-9.5"/><path d="M9.5 20v-5.5h5V20"/><path d="M3 9.5a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/>',
    "stretch": '<path d="M1.5 18h21"/><path d="M3.5 18v3M20.5 18v3"/><path d="M2.5 15.8h11.5"/><path d="M20.2 18V9.4"/><path d="M18.6 9.4h3.2"/><circle cx="4.9" cy="11.6" r="2.1"/><path d="M7.3 13.3h5.4l3-5.6 3.7 2.2"/><path d="M8.6 13.3l2.6-2.4"/>',
    "clipboard": '<rect x="5" y="4" width="14" height="17.5" rx="2"/><path d="M9 2.5h6v3.5H9z"/><path d="M8.5 11h7M8.5 15h4.5"/><path d="m14 19 5-5 1.5 1.5-5 5H14z"/>',
    "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="m21.5 7-9.5 6.5L2.5 7"/>',
    "heart": '<path d="M19.5 13.6C21 12 22 10.5 22 8.6A5.1 5.1 0 0 0 16.9 3.5c-1.9 0-3.3.9-4.9 2.6-1.6-1.7-3-2.6-4.9-2.6A5.1 5.1 0 0 0 2 8.6c0 1.9 1 3.4 2.5 5L12 21z"/>',
    "posture": '<circle cx="12" cy="4" r="2"/><path d="M12 7.5v8"/><path d="M8 10.5h8"/><path d="m12 15.5-3 6M12 15.5l3 6"/>',
    "core": '<path d="M7.5 3c0 4.5 2 6 2 9s-2 4.5-2 9"/><path d="M16.5 3c0 4.5-2 6-2 9s2 4.5 2 9"/><path d="M10.5 9.5h3M10 12.5h4M10.5 15.5h3"/>',
    "body": '<path d="M9 2.5c-1.5 4 .8 6.5.8 9.5S7 17 8.5 21.5"/><path d="M15 2.5c1.5 4-.8 6.5-.8 9.5s2.8 5 1.3 9.5"/><path d="M10.5 13.5c1 .7 2 .7 3 0"/>',
    "lotus": '<path d="M12 20c-4.4 0-8.2-2.2-9-6.2 3.3-.9 6.5.3 9 3.2 2.5-2.9 5.7-4.1 9-3.2-.8 4-4.6 6.2-9 6.2z"/><path d="M12 17c-2.2-2.2-3-5.5-1.8-9.5L12 9.3l1.8-1.8C15 11.5 14.2 14.8 12 17z"/>',
    "sparkle": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15.5l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "smile": '<circle cx="12" cy="12" r="9.5"/><path d="M8 14.5s1.5 2 4 2 4-2 4-2"/><path d="M9 9.5h.01M15 9.5h.01"/>',
    "mat": '<path d="M3 17.5h13.5a4.5 4.5 0 0 0 0-9H7.5a4.5 4.5 0 0 0 0 9"/><circle cx="7.5" cy="13" r="2"/><path d="M16.5 8.5V6"/>',
    # 料金ページ：マンツーマン（2人、片方がインストラクターで色付き）と初心者マーク
    "pair": '<circle cx="7" cy="8.5" r="3"/><path d="M2.4 19.5c0-3.4 2-5.6 4.6-5.6s4.6 2.2 4.6 5.6"/><circle cx="17" cy="8.5" r="3" fill="currentColor" fill-opacity=".22"/><path d="M12.4 19.5c0-3.4 2-5.6 4.6-5.6s4.6 2.2 4.6 5.6z" fill="currentColor" fill-opacity=".22"/>',
    "wakaba": '<path d="M12 10l7.5-7V14L12 21.5z" fill="currentColor" stroke="none"/><path d="M4.5 3 12 10l7.5-7V14L12 21.5 4.5 14z"/>',
    "gem": '<path d="M7 4h10l4.5 5.5L12 21 2.5 9.5z"/><path d="M2.5 9.5h19"/><path d="m9.5 4-1.5 5.5L12 21l4-11.5L14.5 4"/>',
    "bag": '<path d="M5.5 8h13l-1 13.5h-11z"/><path d="M9 8a3 3 0 0 1 6 0"/>',
    "shirt": '<path d="M8 3 3 6l2 4 2.5-1V21h9V9l2.5 1 2-4-5-3c0 1.8-1.8 3-4 3S8 4.8 8 3z"/>',
    "bottle": '<path d="M10 2.5h4V5l2 3v12a1.5 1.5 0 0 1-1.5 1.5h-5A1.5 1.5 0 0 1 8 20V8l2-3z"/><path d="M8 12h8"/>',
    "towel": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M5 7.5h14M9 3v4.5"/>',
    "sock": '<path d="M9 2.5h6.5v8.5l2.7 4.2a3.2 3.2 0 0 1-2.1 4.9l-4.8.9a3.2 3.2 0 0 1-3.5-2l-1-2.6L9 11z"/><path d="M9 6h6.5"/>',
    "yen": '<path d="m6 3 6 8 6-8"/><path d="M12 11v10M7 13.5h10M7 17.5h10"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="2"/><path d="M2.5 10h19M6.5 15h4"/>',
    "phone": '<rect x="6" y="2" width="12" height="20" rx="2.5"/><path d="M11 18h2"/>',
    "lock": '<rect x="4.5" y="10.5" width="15" height="11" rx="2"/><path d="M8 10.5V7a4 4 0 0 1 8 0v3.5"/>',
    "help": '<circle cx="12" cy="12" r="9.5"/><path d="M9.3 9a2.8 2.8 0 0 1 5.4 1c0 1.9-2.7 2.5-2.7 4"/><path d="M12 17.5h.01"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r=".9" fill="currentColor" stroke="none"/>',
    "line": '<path d="M12 3.5c-5.2 0-9 3.3-9 7.3 0 3.4 2.7 6.2 6.6 7l-.5 2.7c-.1.5.4.8.8.6l4.3-2.9c4.4-.4 7.8-3.6 7.8-7.4 0-4-3.8-7.3-9-7.3z"/><path d="M7.3 9v3.7h2M11 9v3.7M13 12.7V9l2.6 3.7V9M19 9h-1.9v3.7H19M17.1 10.85H19"/>',
    "external": '<path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M19 14v5a1.5 1.5 0 0 1-1.5 1.5h-12A1.5 1.5 0 0 1 4 19V6.5A1.5 1.5 0 0 1 5.5 5H10"/>',
    "shield": '<path d="M12 21.5s8-3.5 8-10V5l-8-2.5L4 5v6.5c0 6.5 8 10 8 10z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
}


def icon(name, cls=""):
    c = f"ico {cls}".strip()
    return f'<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


def logo():
    w, h = png_size(os.path.join(IMG_DIR, "logo.png"))
    url = img_url("logo.png")
    return f'<a class="logo" href="/"><img src="{url}" alt="{BRAND}" width="{w}" height="{h}"></a>'


def btn(href, label, cls="btn--pink", ext=False, ico="arrow"):
    target = ' target="_blank" rel="noopener"' if ext else ""
    return f'<a class="btn {cls}" href="{href}"{target}>{label}{icon(ico)}</a>'


def trial_btn(label="無料体験を予約する", cls="btn--pink"):
    return btn(TRIAL, label, cls, ext=True)


# ---------------------------------------------------------------- layout
def header(current):
    cur = ' aria-current="page"'
    items = "".join(
        f'<li><a href="{u}"{cur if u == current else ""}>{t}</a></li>' for u, t, _ in NAV
    )
    drawer = "".join(f'<li><a href="{u}">{t}<small>{e}</small></a></li>' for u, t, e in NAV)
    return f"""<header class="site-header">
  <div class="header-inner">
    {logo()}
    <nav class="gnav" aria-label="グローバルナビゲーション"><ul>{items}</ul></nav>
    <div class="header-cta">{trial_btn()}</div>
    <button class="menu-toggle" type="button" aria-label="メニューを開く" aria-expanded="false" aria-controls="drawer"><span></span><span></span><span></span></button>
  </div>
</header>
<div class="drawer" id="drawer">
  <nav aria-label="スマートフォン用メニュー"><ul>{drawer}</ul></nav>
  <div class="drawer__cta">
    {trial_btn("無料体験を予約する")}
    {btn(MEMBER, "会員の方の予約・変更", "btn--outline", ext=True)}
  </div>
  <ul class="drawer__sns sns" style="--c:var(--teal-d)">
    <li><a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram" style="background:var(--teal-l);color:var(--teal-d)">{icon("instagram")}</a></li>
    <li><a href="{LINE}" target="_blank" rel="noopener" aria-label="LINE公式アカウント" style="background:var(--teal-l);color:var(--teal-d)">{icon("line")}</a></li>
  </ul>
</div>"""


CTA_VARIANTS = {
    "home": ("sub", "＼ カラダが変わると、毎日が変わる ／", "ONE STEPで、理想の自分に出会いませんか？"),
    "about": ("hand", "ピラティスで、もっと好きなわたしに。", "はじめての方でも安心してご参加いただけます。"),
    "news": ("sub", "＼ 自分らしく、少しずつ。 ／", "キャンペーン中の今がはじめどき。お気軽にお越しください。"),
    "price": ("sub", "＼ 体験レッスンは0円 ／", "入会金0円キャンペーン実施中。まずはスタジオの雰囲気を体感してください。"),
    "flow": ("hand", "カラダが変わると、毎日が変わる。", "WEBから24時間いつでもかんたんにご予約いただけます。"),
    "faq": ("sub", "＼ 不安が解消したら、次は体験へ ／", "インストラクターが丁寧にサポートします。"),
    "contact": ("sub", "＼ カラダが変わると、毎日が変わる ／", "平尾店・赤坂店どちらでも体験いただけます。"),
    "legal": ("sub", "＼ 今日の一歩が、明日のわたしを変える ／", "女性専用・少人数制のマシンピラティスをはじめませんか？"),
}


def cta_band(variant):
    kind, top, text = CTA_VARIANTS[variant]
    top_html = f'<p class="cta-band__hand">{top}</p>' if kind == "hand" else f'<p class="cta-band__sub">{top}</p>'
    return f"""<section class="cta-band" aria-label="無料体験のご案内">
  <div class="cta-band__img">{img("cta-woman.jpg", "笑顔でピラティスを楽しむ女性")}</div>
  <div class="cta-band__deco" aria-hidden="true">{img("logo-sign.jpg", "")}<img class="cta-band__leaves" src="/assets/img/leaves.svg" alt=""></div>
  <div class="cta-band__body">
    <div class="cta-band__copy reveal">
      {top_html}
      <p class="cta-band__ttl">まずは<span class="pink">無料体験</span>から。</p>
      <p class="cta-band__text">{text}</p>
      {trial_btn("無料体験を予約する", "btn--pink btn--lg")}
    </div>
    <ul class="cta-band__badges reveal"><li>手ぶらで<br>OK</li><li>お仕事帰り<br>でも</li><li>初心者<br>大歓迎</li></ul>
  </div>
</section>"""


def footer():
    nav = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t, _ in NAV)
    stores = "".join(
        f"<p><b>{s['name']}</b>〒{s['zip']} <span>{s['locality']}{s['street'].split(' ', 1)[0]}</span> <span>{s['street'].split(' ', 1)[1]}</span></p>"
        for s in STORES
    )
    legal = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in [
        ("/policy/", "プライバシーポリシー"), ("/terms/", "利用規約"), ("/law/", "特定商取引法に基づく表記")])
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div>
        {logo()}
        <p class="footer-tagline">今日の一歩が、明日のわたしを変える。<br><span>福岡市中央区 平尾・赤坂の</span><span>女性専用ピラティススタジオ</span></p>
      </div>
      <div>
        <nav class="footer-nav" aria-label="フッターナビゲーション"><ul>{nav}</ul></nav>
        <div class="footer-buttons">
          {btn(TRIAL, "新規レッスン体験予約", "btn--white", ext=True)}
          {btn(MEMBER, "会員の方 予約・変更", "btn--ghost", ext=True)}
        </div>
      </div>
    </div>
    <div class="footer-info">
      <address class="footer-stores">{stores}</address>
      <ul class="footer-legal">{legal}</ul>
      <ul class="sns">
        <li><a href="{INSTAGRAM}" target="_blank" rel="noopener" aria-label="Instagram">{icon("instagram")}</a></li>
        <li><a href="{LINE}" target="_blank" rel="noopener" aria-label="LINE公式アカウント">{icon("line")}</a></li>
      </ul>
    </div>
    <p class="footer-copy"><small>&copy; {BRAND} All Rights Reserved.</small></p>
  </div>
</footer>
<nav class="float-bar" aria-label="予約メニュー">
  <a href="{TRIAL}" target="_blank" rel="noopener">{icon("calendar")}無料体験を予約</a>
  <a href="{MEMBER}" target="_blank" rel="noopener">会員の方はこちら</a>
</nav>"""


def org_ld():
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": SITE + "/#organization",
        "name": BRAND,
        "alternateName": ["ピラティス ワンステップ", "ピラティスワンステップ"],
        "url": SITE + "/",
        "logo": SITE + "/assets/img/logo.png",
        "sameAs": [INSTAGRAM, LINE],
    }


def store_ld(s):
    return {
        "@context": "https://schema.org",
        "@type": ["HealthClub", "SportsActivityLocation"],
        "@id": f"{SITE}/#studio-{s['key']}",
        "name": f"{BRAND} {s['name']}",
        "description": f"福岡市中央区{s['area']}の女性専用・少人数制（最大6名）マシンピラティススタジオ。1回50分、初心者歓迎。{s['desc']}",
        "url": f"{SITE}/#studio-{s['key']}",
        "image": f"{SITE}/assets/img/{s['img']}",
        "priceRange": "¥4,400〜¥13,200",
        "address": {
            "@type": "PostalAddress",
            "postalCode": s["zip"],
            "addressRegion": s["region"],
            "addressLocality": s["locality"],
            "streetAddress": s["street"],
            "addressCountry": "JP",
        },
        "areaServed": [{"@type": "Place", "name": f"福岡市中央区{a}"} for a in s["areas"]],
        "parentOrganization": {"@id": SITE + "/#organization"},
        "sameAs": [INSTAGRAM],
    }


def page(path, title, desc, body, current=None, lds=(), og_image="hero-studio-class.jpg", og_type="website", preload=None, noindex=False, head_extra=""):
    url = SITE + path
    ld_html = "\n".join(
        f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' for ld in lds
    )
    pre = f'<link rel="preload" as="image" href="{img_url(preload)}" fetchpriority="high">' if preload else ""
    doc = f"""<!DOCTYPE html>
<html lang="ja">
<head>
{GTM_HEAD}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">{'<meta name="robots" content="noindex">' if noindex else ""}
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#4fbdb5">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/img/{og_image}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
{FAVICON_LINKS}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Great+Vibes&family=Klee+One:wght@600&family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@500;600;700&display=swap">
{pre}
<link rel="stylesheet" href="/assets/css/style.css?v={ASSET_VER}">
{head_extra}
{ld_html}
{GTAG}
</head>
<body>
{GTM_BODY}
{header(current)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/main.js?v={ASSET_VER}" defer></script>
</body>
</html>
"""
    dest = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(doc)
    if not noindex:
        SITEMAP.append(path)


SITEMAP = []


def sec_title(jp, sub="", en="", cls=""):
    en_html = f'<span class="en">{en}</span>' if en else ""
    sub_html = f"<p>{sub}</p>" if sub else ""
    return f'<div class="sec-title {cls} reveal">{en_html}<h2>{jp}</h2>{sub_html}</div>'


def sub_hero(variant, image, alt, en, h1, h1_small="", lead="", extra_top="", badge="", en_cls=""):
    small = f"<small>{h1_small}</small>" if h1_small else ""
    lead_html = f'<div class="hero__rule"></div><p class="hero__lead">{lead}</p>' if lead else ""
    badge_html = f'<p class="hero__badge"><span>{badge}</span></p>' if badge else ""
    en_html = f'<p class="hero__en {en_cls}" aria-hidden="true">{en}</p>' if en else ""
    return f"""<section class="hero hero--{variant}">
  <img class="leaves leaves--tl" src="/assets/img/leaves.svg" alt="" aria-hidden="true">
  <div class="hero__media">{img(image, alt, eager=True)}</div>
  <div class="hero__body"><div class="hero__inner">
    {extra_top}{en_html}<h1>{h1}{small}</h1>{lead_html}
  </div></div>
  {badge_html}
</section>"""


# ---------------------------------------------------------------- shared blocks
def stores_block(title_tag="h2", stack=False, with_title=True, note=True):
    cards = []
    for s in STORES:
        cards.append(f"""<article class="card store reveal" id="studio-{s['key']}">
  {img(s['img'], f"PILATES ONE STEP {s['name']}のスタジオ内観（{s['area']}）")}
  <div class="store__body">
    <h3>{s['name']}<span>{s['en']}</span></h3>
    <address>{icon("pin")}<span>〒{s['zip']}<br>{s['locality']}{s['street'].split(' ', 1)[0]}<br>{s['street'].split(' ', 1)[1]}</span></address>
    <a class="store__map" href="{map_url(s)}" target="_blank" rel="noopener">Googleマップで見る{icon("external")}</a>
  </div>
</article>""")
    t = sec_title("スタジオのご案内" if with_title == True else with_title, "", "STUDIO", "sec-title--teal") if with_title else ""
    n = '<p class="store-note reveal">駅近で通いやすい、清潔感のあるスタジオです</p>' if note else ""
    return f'{t}{n}<div class="store-grid{" store-grid--stack" if stack else ""}">{"".join(cards)}</div>'


# ---------------------------------------------------------------- news data
NEWS = [
    {
        "id": "269", "date": "2026-10-29", "cat": "news",
        "title": "月額13,200円の「通い放題プラン」が始まりました（既存会員様は12月より適用）",
        "short": "新料金プラン「通い放題」スタート",
        "excerpt": "月に何回通っても月額13,200円（税込）。回数を気にせず、自分のペースで続けられる新プランです。",
        "img": "ring-group-row.jpg",
        "body": """<p>いつもPILATES ONE STEPをご利用いただき、ありがとうございます。<br>このたび、月に何回通っても料金は月額13,200円（税込）のみの「通い放題プラン」をご用意しました。回数を気にせず、ご自分のペースでピラティスを続けていただけます。</p>
<h2>プラン内容</h2>
<div class="price-box"><ul><li>料金：月額13,200円（税込）</li><li>回数：月に何回でも通い放題（1日1回まで）</li></ul></div>
<h2>適用開始</h2>
<ul><li>新規ご入会のお客様：2026年10月29日よりご利用いただけます</li><li>既存会員の皆さま：2026年12月より適用となります</li></ul>
<p>現在ご利用中の会員の皆さまには、12月から本プランをご利用いただけるよう準備を進めております。詳しくはスタジオにてご案内いたしますので、ご不明な点はお気軽にスタッフまでお声がけください。</p>
<h2>こんな方におすすめ</h2>
<ul><li>まずはしっかり通って、体の変化を感じたい</li><li>回数を数えずに、気軽に通いたい</li><li>運動を習慣にしたい</li></ul>
<p>「ピラティスは初めて」という方も大歓迎です。インストラクターが一人ひとりに合わせて丁寧にサポートいたしますので、安心してお越しください。</p>
<p>皆さまのご来店を、スタッフ一同心よりお待ちしております。</p>""",
        "actions": True,
    },
    {
        "id": "255", "date": "2026-04-28", "cat": "store",
        "title": "PILATES ONE STEP 赤坂店 6月1日OPEN！",
        "short": "赤坂店 6月1日OPEN！",
        "excerpt": "2号店となる赤坂店が、けやき通りエリアにオープン。赤坂・警固エリアからも通いやすいスタジオです。",
        "img": "studio-akasaka.jpg", "script": "New Open!",
        "body": """<p>いつもPILATES ONE STEPをご利用いただき、誠にありがとうございます。<br>このたび、2号店となる「PILATES ONE STEP 赤坂店」を2026年6月1日にオープンすることとなりました。</p>
<p>より多くの皆さまにピラティスを通じて「整う時間」をお届けできるよう、新たな拠点としてスタートいたします。</p>
<h2>所在地</h2>
<p>〒810-0042 福岡市中央区赤坂3-11-41<br>ルネッサンス21赤坂けやき通り 2F</p>
<p>ご入会・体験レッスンのご予約は、専用の予約サイトより簡単にお手続きいただけます。平尾店同様、はじめての方でも安心してご参加いただける体験レッスンもご用意しています。</p>""",
        "actions": True,
    },
    {
        "id": "229", "date": "2025-11-06", "cat": "news",
        "title": "おかげさまで、オープンから2ヶ月を迎えました！",
        "short": "オープンから2ヶ月を迎えました！",
        "excerpt": "たくさんのご来店ありがとうございます。これからも安心して通えるスタジオを目指してまいります。",
        "img": "small-group-ring.jpg",
        "body": """<p>いつもPILATES ONE STEPをご利用いただき、誠にありがとうございます。</p>
<p>9月のオープンから2ヶ月が経ち、多くの方にご来店いただいております。たくさんの新しい出会いに感謝しつつ、これからも皆さまが安心して通えるスタジオを目指してまいります。</p>
<p>今後も引き続き、PILATES ONE STEPをよろしくお願いいたします。</p>""",
        "gallery": ["ring-kneeling-class.jpg", "reformer-posture.jpg", "core-reformer-class.jpg"],
    },
    {
        "id": "215", "date": "2025-09-01", "cat": "store",
        "title": "PILATES ONE STEP 本日NEW OPEN!!",
        "short": "平尾店 本日NEW OPEN!!",
        "excerpt": "平尾・薬院・高宮エリアの女性専用マシンピラティススタジオが本日オープンしました。",
        "img": "studio-hirao.jpg",
        "body": """<p>平尾・薬院・高宮エリアの女性専用マシンピラティススタジオ、PILATES ONE STEPが本日オープンいたしました！</p>
<p>「いつまでも美しくあり続けたい」そんな女性のために、少人数制で安心して取り組めるレッスンをご用意しております。</p>
<p>オープンを記念して、「体験レッスン」「入会金」「初月会費」が0円になる特別キャンペーンを開催中です。初めての方でも無理なく始められるプログラムですので、この機会にぜひ新しい一歩を踏み出してみてください。</p>
<p>皆さまのご来店を、心よりお待ちしております。</p>""",
        "actions": True,
    },
    {
        "id": "187", "date": "2025-07-29", "cat": "campaign",
        "title": "9月1日NEW OPEN！体験レッスン・入会金・初月会費が0円キャンペーン",
        "short": "オープン記念 0円キャンペーン",
        "excerpt": "オープン記念として、体験レッスン・入会金・初月会費が0円になるキャンペーンを実施しました。",
        "img": "beginner-support.jpg",
        "body": """<p>女性専用・少人数制のマシンピラティススタジオ「PILATES ONE STEP」が、2025年9月1日、福岡市中央区平尾エリアに新しくオープンします。</p>
<p>「一歩ずつ、自分らしい輝きを」というコンセプトのもと、初心者の方も安心してスタートできるよう、丁寧なサポートと快適な空間をご用意しました。</p>
<h2>女性専用・少人数制・マシンピラティスの特長</h2>
<ul><li>女性専用：周りを気にせず集中できる空間で、安心してレッスンに参加可能。</li><li>少人数制：一人ひとりに合わせた指導ができるので、初心者でもしっかりサポート。</li><li>マシンピラティス：リフォーマーを使用し、体幹強化・姿勢改善・柔軟性アップに効果的。</li></ul>
<p>「ピラティスが初めて」「運動が苦手」という方でも無理なく始められます。</p>
<h2>オープン記念！期間限定「0円キャンペーン」</h2>
<div class="price-box"><ul><li>体験レッスン　0円</li><li>入会金　0円</li><li>初月会費　0円</li></ul></div>
<p>※本キャンペーンは2025年9月末で終了しました。現在の料金・キャンペーンは<a href="/price/" style="color:var(--teal-d);text-decoration:underline">料金ページ</a>をご覧ください。</p>""",
        "actions": False,
    },
]
NEWS_PER_PAGE = 8  # お知らせ一覧の1ページあたりのカード数（2列なので偶数に。先頭の大きな記事は別枠）
CAT_LABEL = {"news": "お知らせ", "store": "店舗情報", "campaign": "キャンペーン"}


def cat_tag(c):
    return f'<span class="cat cat--{c}">{CAT_LABEL[c]}</span>'


def fmt_date(d):
    return d.replace("-", ".")


# トップの手書き風キャッチ（Illustratorで作成した image/catch01.svg）
CATCH_TEXT = "今日の一歩が、明日のわたしを変える。"


def hero_catch():
    return f'<p class="hero-catch">{svg_img("catch01.svg", CATCH_TEXT)}</p>'


# Illustratorで作成したSVGを、viewBoxの縦横比つきの<img>として出力する
def svg_img(name, alt, cls=""):
    vb = re.search(r'viewBox="([\d.\s-]+)"', open(os.path.join(IMG_DIR, name), encoding="utf-8").read()).group(1).split()
    w, h = round(float(vb[2])), round(float(vb[3]))
    cls_attr = f' class="{cls}"' if cls else ""
    return f'<img{cls_attr} src="{img_url(name)}" alt="{alt}" width="{w}" height="{h}">'


# 「好きなだけ通える」の手書き風サブキャッチ（PCは image/subcatch.svg、スマホは1行の image/subcatch01.svg）
def sub_catch():
    vb = re.search(r'viewBox="([\d.\s-]+)"', open(os.path.join(IMG_DIR, "subcatch01.svg"), encoding="utf-8").read()).group(1).split()
    w, h = round(float(vb[2])), round(float(vb[3]))
    return (f'<span class="suki-row"><picture><source media="(max-width: 520px)" srcset="{img_url("subcatch01.svg")}" width="{w}" height="{h}">'
            f'{svg_img("subcatch.svg", "好きなだけ通える", "suki")}</picture></span>')


# ================================================================= TOP
def build_home():
    features = [
        ("ring-smile.jpg", "woman", "女性専用", "周りを気にせず、<wbr>自分のペースで<wbr>通えます。", "女性インストラクターと笑顔でレッスンを受ける女性"),
        ("small-group-ring.jpg", "users", "少人数制レッスン", "最大6名までの<wbr>少人数制。<wbr>丁寧なサポートで、<wbr>初めての方でも<wbr>安心です。", "少人数制のマシンピラティスレッスン"),
        ("feature-50min.jpg", "clock", "1回50分", "無理なく<wbr>続けられる、<wbr>ちょうどいい<wbr>レッスン時間です。", "時計とレッスンを受ける女性たち"),
        ("beginner-support.jpg", "sprout", "初心者歓迎", "初めての方も、<wbr>インストラクターが<wbr>基礎からサポート。", "インストラクターが初心者の動きをサポートする様子"),
    ]
    f_html = "".join(
        f'<article class="card feature reveal">{img(i, alt)}<div>{icon(ic)}<h3>{t}</h3><p>{d}</p></div></article>'
        for i, ic, t, d, alt in features
    )
    lessons = [
        ("lesson-basic.jpg", "ベーシック", "姿勢から学べる基礎クラス。<br>はじめての方はまずここから。", "腕を伸ばしてレッスンを受ける女性たち"),
        ("lesson-posture.jpg", "美姿勢", "背骨と骨盤を整え、美しい立ち姿へ。<br>猫背や巻き肩が気になる方に。", "背筋を伸ばして座る女性の後ろ姿"),
        ("lesson-legs.jpg", "美脚・ヒップアップ", "下半身を引き締め、理想のラインへ導きます。", "リフォーマーのバーに足をのせた足元"),
        ("core-reformer-class.jpg", "お腹引き締め", "体幹を鍛え、スッキリとしたウエストへ。", "お腹まわりを引き締める体幹レッスン"),
        ("private-lesson.jpg", "プライベートレッスン", "マンツーマンで、<br>目的に合わせてしっかりサポート。", "インストラクターとのマンツーマンレッスン"),
    ]
    l_html = "".join(
        f'<article class="lesson reveal">{img(i, alt)}<h3>{t}</h3><p>{d}</p></article>' for i, t, d, alt in lessons
    )
    steps = [
        ("calendar", "予約", "WEBから24時間いつでも<br>かんたん予約"),
        ("store", "ご来店", "手ぶらでOK！<br>レッスン10分前にお越しください"),
        ("stretch", "体験レッスン", "実際のレッスンを<br>50分間体験"),
        ("clipboard", "ご入会", "気に入っていただけたら<br>オンラインで入会手続き"),
    ]
    s_html = "".join(
        f'<li class="card step reveal"><span class="step__num">{i + 1:02d}</span>{icon(ic)}<h3>{t}</h3><p>{d}</p></li>'
        for i, (ic, t, d) in enumerate(steps)
    )
    news_rows = "".join(
        f'<li><a href="/news/{n["id"]}/"><time datetime="{n["date"]}">{fmt_date(n["date"])}</time>{cat_tag(n["cat"])}<span class="ttl">{esc(n["title"])}</span>{icon("chev")}</a></li>'
        for n in NEWS[:3]
    )
    store_tiles = "".join(
        f'<a class="store-tile" href="#studio-{s["key"]}">{img(s["img"], s["name"] + "のスタジオ", eager=True)}'
        f'<span class="store-tile__label"><span class="script" aria-hidden="true">{s["en"].capitalize()}</span><b>{s["name"]}</b></span></a>'
        for s in STORES
    )

    body = f"""<section class="home-hero">
  <img class="leaves leaves--tl" src="/assets/img/leaves.svg" alt="" aria-hidden="true">
  <div class="home-hero__media">{img("hero-studio-class.jpg", "PILATES ONE STEPのスタジオでマシンピラティスをする女性たち", eager=True)}
    <svg class="home-hero__wave" viewBox="0 0 681 120" preserveAspectRatio="none" aria-hidden="true">
      <path class="home-hero__wave-back" d="M0,92 C60,62 130,42 210,42 C330,42 380,62 470,58 C560,54 630,30 681,4 L681,120 L0,120 Z"/>
      <path class="home-hero__wave-front" d="M0,120 C60,90 120,52 210,46 C330,40 400,66 490,68 C570,70 630,50 681,38 L681,120 L0,120 Z"/>
    </svg>
  </div>
  <div class="home-hero__body">
    <div class="home-hero__copy">
      {hero_catch()}
      <h1><small>福岡市中央区 平尾・赤坂</small><span class="home-hero__title">女性専用<br><span class="home-hero__title-line">ピラティススタジオ</span></span></h1>
      <ul class="home-hero__badges">
        <li>{icon("users")}<b>少人数制<br>レッスン</b><span class="cap">最大<em>6</em>名まで</span></li>
        <li>{icon("woman")}<b>女性専用</b><span class="cap">安心して<br>通える環境</span></li>
        <li>{icon("pin")}<b>2店舗</b><span class="cap">どちらも<br>利用OK</span></li>
      </ul>
      <div class="home-hero__offer">
      <div class="home-hero__price">
        {sub_catch()}
        <span class="label">月額</span><span class="num">13,200<small>円</small></span><span class="tax">（税込）</span>
      </div>
      <ul class="checks">
        <li>{icon("check")}1日1回まで受講可能</li>
        <li>{icon("check")}月額定額で好きなレッスンを受講できます</li>
      </ul>
      </div>
      {trial_btn("まずは無料体験を予約する", "btn--pink btn--lg")}
    </div>
    <div class="home-hero__stores">{store_tiles}</div>
  </div>
  <p class="scroll-sign" aria-hidden="true">SCROLL</p>
</section>

<section class="section section--soft" id="features">
  <div class="container">
    {sec_title("ONE STEPの魅力", "女性が安心して通える、続けやすい環境が整っています。", "FEATURES", "sec-title--teal")}
    <div class="feature-grid">{f_html}</div>
  </div>
</section>

<section class="section section--even" id="lesson">
  <div class="container">
    {sec_title("目的に合わせたレッスン内容", "なりたい自分に合わせて選べる、豊富なレッスンをご用意しています。", "LESSON")}
    <div class="lesson-grid">{l_html}</div>
  </div>
</section>

<section class="section section--soft" id="price">
  <div class="container">
    {sec_title("料金プラン", "続けやすいシンプルな料金プランをご用意しています。", "PRICE")}
    <div class="price-cards">
      <article class="pc pc--main reveal">
        <p class="pc__lead">好きなだけ通えて、しっかり変わる！</p>
        <h3 class="pc__ttl"><span class="burst">通い放題</span></h3>
        <p class="pc__price"><span class="pc__unit">月額</span><span class="pc__num">13,200</span><span class="pc__yen">円</span><span class="pc__tax">（税込）</span></p>
        <ul class="pc__checks"><li>{icon("check")}平尾店・赤坂店どちらも利用OK</li><li>{icon("check")}1日1回まで</li></ul>
      </article>
      <article class="pc pc--trial reveal">
        <p class="pc__lead">まずは気軽に始めたい方に</p>
        <h3 class="pc__ttl">初回体験</h3>
        <p class="pc__price"><span class="burst burst--lg"><span class="pc__num pc__num--xl">0</span><span class="pc__yen">円</span></span></p>
        <span class="pc__pill">手ぶらでOK！</span>
      </article>
      <article class="pc pc--private reveal">
        <div class="pc__bg" aria-hidden="true">{img("studio-hirao.jpg", "")}</div>
        <p class="pc__lead">マンツーマンでしっかりサポート</p>
        <h3 class="pc__ttl">プライベートレッスン</h3>
        <div class="pc__lower">
          <p class="pc__price"><span class="pc__unit">1回</span><span class="pc__num">4,400</span><span class="pc__yen">円</span><span class="pc__tax">（税込）</span></p>
          <p class="pc__note">目的に合わせた<br>オーダーメイドレッスン</p>
        </div>
        {img("private-cutout.png", "インストラクターがマンツーマンでフォームをサポートする様子", "pc__person")}
      </article>
    </div>
    <p class="center" style="margin-top:30px"><a class="link-more" href="/price/">料金の詳細を見る{icon("arrow")}</a></p>
  </div>
</section>

<section class="section" id="flow">
  <div class="container">
    {sec_title("ご入会までの流れ", "かんたん4ステップで、すぐに始められます。", "FLOW")}
    <ol class="steps" style="list-style:none">{s_html}</ol>
    <p class="center" style="margin-top:34px"><a class="link-more" href="/flow/">体験の流れを詳しく見る{icon("arrow")}</a></p>
  </div>
</section>

<section class="section section--soft" id="studio">
  <div class="container">
    {stores_block()}
    <p class="center note" style="margin-top:24px">平尾店は薬院・高宮から、赤坂店は警固・けやき通り周辺からも通いやすい立地です。</p>
  </div>
</section>

<section class="section" id="news">
  <div class="container--narrow">
    {sec_title("お知らせ", "", "NEWS")}
    <ul class="news-rows reveal">{news_rows}</ul>
    <p class="center" style="margin-top:30px"><a class="link-more" href="/news/">お知らせ一覧へ{icon("arrow")}</a></p>
  </div>
</section>

{cta_band("home")}"""
    website_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": BRAND,
        "url": SITE + "/",
        "inLanguage": "ja",
        "publisher": {"@id": SITE + "/#organization"},
    }
    page(
        "/",
        "女性専用・少人数制マシンピラティス｜福岡市中央区 平尾・赤坂｜PILATES ONE STEP",
        "福岡市中央区の女性専用・少人数制マシンピラティススタジオ「PILATES ONE STEP」。1レッスン最大6名。平尾店（薬院・高宮エリア）と赤坂店（警固エリア）の2店舗を利用でき、月額13,200円で通い放題。1回50分・初心者歓迎、無料体験レッスン受付中。",
        body, "/", [org_ld(), website_ld] + [store_ld(s) for s in STORES], preload="hero-studio-class.jpg", head_extra=PRICE_FONT,
    )


# ================================================================= ABOUT
def build_about():
    commits = [
        ("ring-smile.jpg", "woman", "女性専用", "周りを気にせず、<br>自分のペースで集中できます。", "女性専用スタジオでリングを使ったレッスン"),
        ("about-group.jpg", "users", "少人数制・予約制", "一人ひとりに目が届く環境で、<br>丁寧にサポートします。", "少人数でレッスンを受ける女性たち"),
        ("reformer-leg-strap.jpg", "clock", "1回50分", "無理なく続けやすい、<br>ちょうどいいレッスン時間。", "50分のマシンピラティスレッスン"),
    ]
    c_html = "".join(
        f'<article class="card commit reveal">{img(i, alt)}<div class="commit__body"><span class="commit__icon">{icon(ic)}</span><h3>{t}</h3><p>{d}</p></div></article>'
        for i, ic, t, d, alt in commits
    )
    charms = [
        ("side-stretch-closeup.jpg", "posture", "姿勢を整える", "美しい姿勢で、<br>毎日をもっと快適に。", "姿勢を整えるストレッチ"),
        ("cadillac-roll.jpg", "core", "体幹を鍛える", "ブレないカラダで、<br>動きやすく疲れにくく。", "キャデラックで体幹を鍛えるエクササイズ"),
        ("lesson-posture.jpg", "body", "しなやかな<wbr>ボディラインへ", "無理なく引き締めて、<br>女性らしいラインに。", "背筋を伸ばして座る女性の後ろ姿"),
        ("about-refresh.jpg", "lotus", "心もリフレッシュ", "深い呼吸で、<br>心まで軽やかに。", "スタジオのカウンターに置かれた水とタオル"),
    ]
    ch_html = "".join(
        f'<article class="card charm reveal">{img(i, alt)}<div class="commit__body"><span class="commit__icon">{icon(ic)}</span><h3>{t}</h3><p>{d}</p></div></article>'
        for i, ic, t, d, alt in charms
    )
    recs = [
        ("about01.png", "運動が苦手", "体力に自信がなくても<br>大丈夫です。"),
        ("about02.png", "姿勢を整えたい", "猫背や肩こりを<br>改善したい方に。"),
        ("about03.png", "身体を引き締めたい", "しなやかで<br>メリハリのあるカラダへ。"),
        ("about04.png", "無理なく続けたい", "忙しい毎日でも<br>自分のペースで通えます。"),
    ]
    def rec_img(src):
        # 縮小後の画像を、さらに半分の大きさで表示する（高解像度画面でもくっきり見せるため）
        w, h = png_size(os.path.join(IMG_DIR, src))
        return img(src, "").replace(f'width="{w}" height="{h}"', f'width="{w // 2}" height="{h // 2}"')

    r_html = "".join(
        f'<article class="card recommend reveal"><div class="recommend__icon">{rec_img(ic)}</div><h3>{t}</h3><p>{d}</p></article>'
        for ic, t, d in recs
    )
    body = f"""{sub_hero("about", "about-hero.jpg", "朝の光が差すスタジオとヨガマット", "",
        "わたしの日常に、<br>ピラティスを。", "福岡・平尾／赤坂の女性専用マシンピラティス",
        "女性専用・最大6名の少人数制・1回50分。<br>初心者の方でも安心して続けられる<br>福岡・平尾／赤坂のマシンピラティススタジオです。",
        extra_top=f'<p class="hero__script hero__script--svg">{svg_img("fight.svg", "がんばりすぎない、わたしらしいカラダと心をつくる。")}</p>')}
<section class="section">
  <img class="branch" src="/assets/img/branch.svg" alt="" aria-hidden="true" style="right:0;top:120px">
  <div class="container">
    {sec_title("ONE STEPについて", "", "ABOUT US")}
    <div class="about-intro">
      <div class="reveal">{img("studio-hirao.jpg", "PILATES ONE STEPのスタジオ全景")}</div>
      <div class="reveal">
        <p>PILATES ONE STEPは、<br>ピラティスを特別なものではなく、<br>毎日に寄り添う習慣にしたいと考えています。<br>無理なく、心地よく、自分らしく<br>続けられる場所を目指しています。</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {sec_title("私たちのこだわり", "", "COMMITMENT")}
    <div class="commit-grid">{c_html}</div>
  </div>
</section>

<section class="section section--soft">
  <div class="container">
    {sec_title("マシンピラティスの魅力", "", "MACHINE PILATES")}
    <p class="machine-lead reveal">マシンピラティスは、リフォーマーなどの専用マシンを使って、身体に負担をかけずに効率よく体幹を鍛え、正しい姿勢を無理なく身につけられるのが魅力です。スプリングの強度や動きを細かく調整できるので、初心者の方でも自分に合ったペースで安心して続けられます。</p>
    <div class="charm-grid" style="margin-top:50px">{ch_html}</div>
  </div>
</section>

<section class="section">
  <div class="container story">
    <article class="card story__logo reveal">
      {img("logo-sign.jpg", "スタジオの壁に掲げたPILATES ONE STEPのダイヤモンドのロゴ")}
      <div>
      <h3>一歩ずつ。自分らしい輝きを。</h3>
      <p>ロゴに描かれているのは、カットされたダイヤモンドのように見える“一歩先”を象徴するモチーフ。角度のあるシルエットは、一人ひとりの異なる個性や輝きを大切にしたいという思いを表しています。線で形づくられた多面体は、心と身体、そしてライフスタイルをつなぐ“軸”の存在。あなたの一歩が未来の大きな変化につながることを信じて、その道のりに寄り添います。</p>
      </div>
    </article>
    <article class="card reveal">
      <h3>安心できる“はじめの一歩”を大切に</h3>
      <p>初心者の方にも安心していただけるよう、「シンプルで体感しやすい」を重視したメニューづくりをしています。全インストラクターが共通のプログラムに基づいて種目・回数・強度を統一し、質の高いレッスンを安定してご提供。飽きのこない豊富なバリエーションで理想の体型をサポートします。その日の気分や体調に合わせてレッスンを選べる自由も、ONE STEPの魅力です。</p>
    </article>
  </div>
</section>

<section class="section section--soft">
  <div class="container">
    {sec_title("こんな方におすすめ", "", "RECOMMEND")}
    <div class="recommend-grid">{r_html}</div>
  </div>
</section>

<section class="section">
  <div class="container">{stores_block(with_title="通いやすい2つのスタジオ")}</div>
</section>

{cta_band("about")}"""
    page(
        "/about/",
        "私たちについて｜福岡・平尾／赤坂の女性専用マシンピラティス｜PILATES ONE STEP",
        "PILATES ONE STEPは「ピラティスを日常に」をコンセプトにした女性専用・少人数制のマシンピラティススタジオです。平尾・薬院・高宮、赤坂・警固エリアから通いやすい2店舗で、初心者の方も安心して続けられます。",
        body, "/about/", [], og_image="about-hero.jpg", preload="about-hero.jpg",
    )


# ================================================================= NEWS
def build_news():
    first, rest = NEWS[0], NEWS[1:]
    feat = f"""<article class="card news-feature news-item reveal" data-cat="{first['cat']}">
  <a class="news-feature__img" href="/news/{first['id']}/">{img(first['img'], first['short'])}{f'<span class="script" aria-hidden="true">{first["script"]}</span>' if first.get("script") else ''}</a>
  <div class="news-feature__body">
    <div class="news-meta"><time datetime="{first['date']}">{fmt_date(first['date'])}</time>{cat_tag(first['cat'])}</div>
    <h2><a href="/news/{first['id']}/">{esc(first['title'])}</a></h2>
    <p>{first['excerpt']}</p>
    <a class="link-more" href="/news/{first['id']}/" style="align-self:flex-start">詳しく見る{icon("arrow")}</a>
  </div>
</article>"""
    cards = "".join(
        f"""<article class="card news-card news-item reveal" data-cat="{n['cat']}">
  <a href="/news/{n['id']}/" tabindex="-1" aria-hidden="true">{img(n['img'], n['short'])}</a>
  <div class="news-card__body">
    <div class="news-meta"><time datetime="{n['date']}">{fmt_date(n['date'])}</time>{cat_tag(n['cat'])}</div>
    <h2><a href="/news/{n['id']}/">{esc(n['title'])}</a></h2>
    <p>{n['excerpt']}</p>
    <a class="link-more" href="/news/{n['id']}/">詳しく見る{icon("arrow")}</a>
  </div>
</article>"""
        for n in rest
    )
    body = f"""{sub_hero("news", "news-hero.jpg", "PILATES ONE STEPのスタジオでのグループレッスン", "NEWS",
        "お知らせ", "", "キャンペーンや店舗情報など、<br>最新のお知らせをお届けします。")}
<section class="section">
  <div class="container">
    <h2 class="sr-only">お知らせ一覧</h2>
    <ul class="news-filter" aria-label="カテゴリで絞り込む">
      <li><button type="button" data-cat="all" aria-pressed="true">すべて</button></li>
      <li><button type="button" data-cat="campaign" aria-pressed="false">キャンペーン</button></li>
      <li><button type="button" data-cat="store" aria-pressed="false">店舗情報</button></li>
      <li><button type="button" data-cat="news" aria-pressed="false">お知らせ</button></li>
    </ul>
    {feat}
    <div class="news-grid">{cards}</div>
    <p class="news-empty" hidden>該当するお知らせはまだありません。</p>
    <nav class="pager" aria-label="お知らせのページ送り" data-per-page="{NEWS_PER_PAGE}" hidden></nav>
  </div>
</section>
{cta_band("news")}"""
    list_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/news/{n['id']}/", "name": n["title"]}
            for i, n in enumerate(NEWS)
        ],
    }
    page(
        "/news/",
        "お知らせ｜キャンペーン・店舗情報｜PILATES ONE STEP（福岡・平尾／赤坂）",
        "福岡市中央区の女性専用ピラティススタジオ PILATES ONE STEP（平尾店・赤坂店）からのお知らせ。キャンペーン情報、新店舗のオープン情報、料金プランのご案内などをお届けします。",
        body, "/news/", [list_ld], og_image="news-hero.jpg", preload="news-hero.jpg",
    )

    for i, n in enumerate(NEWS):
        newer = NEWS[i - 1] if i > 0 else None
        older = NEWS[i + 1] if i + 1 < len(NEWS) else None
        prev_html = f'<a class="prev" href="/news/{older["id"]}/"><small>PREV</small>{esc(older["short"])}</a>' if older else "<span></span>"
        next_html = f'<a class="next" href="/news/{newer["id"]}/"><small>NEXT</small>{esc(newer["short"])}</a>' if newer else "<span></span>"
        actions = ""
        if n.get("actions"):
            actions = f"""<div class="article__actions">
  {btn(TRIAL, "無料体験を予約する", "btn--pink", ext=True)}
  {btn(LINE, "LINEで問い合わせる", "btn--line", ext=True)}
  {btn("/contact/", "フォームで問い合わせる", "btn--outline")}
</div>"""
        gallery = ""
        if n.get("gallery"):
            gallery = '<div class="news-grid" style="grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px">' + "".join(
                img(g, "PILATES ONE STEPのレッスン風景", "") for g in n["gallery"]
            ) + "</div>"
        others = "".join(
            f'<li><a href="/news/{o["id"]}/"><time datetime="{o["date"]}">{fmt_date(o["date"])}</time>{cat_tag(o["cat"])}<span class="ttl">{esc(o["title"])}</span>{icon("chev")}</a></li>'
            for o in NEWS if o is not n
        )[:]
        body = f"""<section class="hero-mini">
  <img class="branch" src="/assets/img/branch.svg" alt="" aria-hidden="true" style="right:4%;top:-10px;width:130px">
  <div class="container"><p class="hero__en" aria-hidden="true">NEWS</p><p class="serif" style="color:var(--navy);letter-spacing:.14em">お知らせ</p></div>
</section>
<section class="section section--tight">
  <div class="container--narrow">
    <article class="card article">
      <div class="news-meta"><time datetime="{n['date']}">{fmt_date(n['date'])}</time>{cat_tag(n['cat'])}</div>
      <h1>{esc(n['title'])}</h1>
      <div class="article__eyecatch">{img(n['img'], n['short'], eager=True)}</div>
      <div class="article__body">{n['body']}{gallery}</div>
      {actions}
    </article>
    <nav class="article-nav" aria-label="前後のお知らせ">{prev_html}<a class="list" href="/news/">一覧へ戻る</a>{next_html}</nav>
  </div>
</section>
<section class="section section--soft section--tight">
  <div class="container--narrow">
    {sec_title("その他のお知らせ", "", "OTHER NEWS")}
    <ul class="news-rows">{others}</ul>
  </div>
</section>
{cta_band("news")}"""
        article_ld = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": n["title"],
            "datePublished": n["date"] + "T10:00:00+09:00",
            "dateModified": n["date"] + "T10:00:00+09:00",
            "image": [f"{SITE}/assets/img/{n['img']}"],
            "mainEntityOfPage": f"{SITE}/news/{n['id']}/",
            "author": {"@type": "Organization", "name": BRAND, "url": SITE + "/"},
            "publisher": {"@id": SITE + "/#organization"},
        }
        page(
            f"/news/{n['id']}/",
            f"{n['title']}｜お知らせ｜PILATES ONE STEP",
            f"{n['excerpt']}福岡市中央区 平尾・赤坂の女性専用ピラティススタジオ PILATES ONE STEPのお知らせです。",
            body, "/news/", [article_ld], og_image=n["img"], og_type="article",
        )


# ================================================================= PRICE
def build_price():
    body = f"""{sub_hero("price", "price-hero.jpg", "スタジオのカウンターに置かれた水とタオル", "PRICE",
        "料金", "福岡・平尾／赤坂の女性専用ピラティス 料金プラン", "通いやすく、続けやすい<br>料金プランをご用意しています。", en_cls="hero__en--teal")}
<section class="section">
  <div class="container">
    <h2 class="sr-only">月額プラン</h2>
    <div class="plan-main reveal">
      <div class="plan-main__body">
        <h3 class="plan-main__name" style="font-family:var(--serif);font-size:clamp(36px,5vw,56px);letter-spacing:.1em;font-weight:700">通い放題</h3>
        <p class="plan-main__price"><span class="m">月額</span><span class="n">13,200</span><span class="y">円</span><span class="t">（税込）</span></p>
        <ul class="checks">
          <li>{icon("check")}1日1回まで受講可能</li>
          <li>{icon("check")}月額定額で好きなレッスンを受講できます</li>
          <li>{icon("check")}平尾店・赤坂店どちらでもご利用いただけます</li>
        </ul>
      </div>
      {img("ring-group-arms.jpg", "通い放題プランでリングを使ったレッスンを受ける女性たち")}
    </div>

    <div class="plan-sub">
      <article class="plan-card plan-card--teal reveal">
        <div class="plan-card__head"><h3 class="plan-card__ttl">{icon("mat")}体験レッスン</h3></div>
        <p class="plan-card__price">0<span class="y">円</span></p>
        <p class="plan-card__text">50分の実際のレッスンを体験。<br>手ぶらでOKです。</p>
        {img("price-trial.jpg", "ベンチに置かれたタオルと靴下と水のボトル")}
        <a class="plan-card__link" href="{TRIAL}" target="_blank" rel="noopener" aria-label="体験レッスンを予約する"><span class="plan-card__arrow">{icon("chev")}</span></a>
      </article>
      <article class="plan-card plan-card--blue reveal">
        <div class="plan-card__head"><h3 class="plan-card__ttl">{icon("pair")}プライベートレッスン</h3></div>
        <p class="plan-card__price"><small>1回</small>4,400<span class="y">円</span><span class="t">（税込）</span></p>
        <p class="plan-card__text">マンツーマンで、目的に合わせた<br>オーダーメイドレッスン。</p>
        {img("instructor-arm-strap.jpg", "インストラクターとのプライベートレッスン")}
        <a class="plan-card__link" href="/contact/" aria-label="プライベートレッスンについて問い合わせる"><span class="plan-card__arrow">{icon("chev")}</span></a>
      </article>
      <article class="plan-card plan-card--pink reveal">
        <span class="plan-card__corner">今だけの入会キャンペーン</span>
        <div class="plan-card__head"><h3 class="plan-card__ttl">{icon("wakaba")}初月入会金</h3></div>
        <p class="plan-card__price">0<span class="y">円</span></p>
        <p class="plan-card__text"><span class="was">通常 <s>11,000円（税込）</s></span>新規ご入会のお客様が対象です。</p>
        {img("logo-sign.jpg", "スタジオの壁のPILATES ONE STEPロゴ")}
        <a class="plan-card__link" href="{REGISTER}" target="_blank" rel="noopener" aria-label="新規入会の手続きへ進む"><span class="plan-card__arrow">{icon("chev")}</span></a>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {sec_title("ご入会について", "", "MEMBERSHIP")}
    <div class="card join-box reveal">
      <a href="{REGISTER}" target="_blank" rel="noopener"><span class="circle">{icon("calendar")}</span><span><strong>ご入会はオンラインで簡単</strong><small>予約サイトから24時間いつでもお手続きいただけます</small></span>{icon("chev", "arrow")}</a>
      <a href="/flow/"><span class="circle">{icon("sprout")}</span><span><strong>初心者の方も安心して<br>ご参加いただけます</strong><small>体験からご入会までの流れを見る</small></span>{icon("chev", "arrow")}</a>
    </div>
  </div>
</section>

<section class="section section--soft">
  <div class="container--narrow">
    {sec_title("お支払いについて", "", "PAYMENT")}
    <dl class="info-list reveal">
      <dt>お支払い方法</dt><dd>クレジットカード決済、オンライン口座振替</dd>
      <dt>お支払い時期</dt><dd>クレジットカード決済：毎月20日に決済<br>オンライン口座振替：毎月27日に引き落とし</dd>
      <dt>月会費の締め日</dt><dd>当月10日締めで、翌月分の月会費をお支払いいただきます。</dd>
      <dt>プラン変更・休会・退会</dt><dd>所定のお手続きが必要です。期限や方法は<a href="/terms/" style="color:var(--teal-d);text-decoration:underline">利用規約</a>・<a href="/faq/#procedure" style="color:var(--teal-d);text-decoration:underline">よくある質問</a>をご確認ください。</dd>
    </dl>
    <p class="note" style="margin-top:14px">※表示価格はすべて税込です。※キャンペーン内容は予告なく変更・終了する場合があります。</p>
  </div>
</section>

{cta_band("price")}"""
    offer_ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": "女性専用マシンピラティス レッスン",
        "provider": {"@id": SITE + "/#organization"},
        "areaServed": ["福岡市中央区平尾", "福岡市中央区薬院", "福岡市中央区高宮", "福岡市中央区赤坂", "福岡市中央区警固"],
        "offers": [
            {"@type": "Offer", "name": "通い放題プラン（月額）", "price": "13200", "priceCurrency": "JPY"},
            {"@type": "Offer", "name": "プライベートレッスン（1回）", "price": "4400", "priceCurrency": "JPY"},
            {"@type": "Offer", "name": "体験レッスン", "price": "0", "priceCurrency": "JPY"},
        ],
    }
    page(
        "/price/",
        "料金｜月額13,200円で通い放題の女性専用ピラティス｜PILATES ONE STEP（福岡・平尾／赤坂）",
        "PILATES ONE STEPの料金プラン。月額13,200円（税込）の通い放題プラン、1回4,400円のプライベートレッスン、体験レッスン0円。今なら入会金0円。平尾店・赤坂店どちらも利用できます。",
        body, "/price/", [offer_ld], og_image="price-hero.jpg", preload="price-hero.jpg",
    )


# ================================================================= FLOW
def build_flow():
    steps = [
        ("flow-reserve-phone.jpg", "calendar", "予約", "WEBからご希望の日時を選んで簡単予約。", "スマートフォンでレッスンを予約する女性"),
        ("studio-hirao.jpg", "store", "ご来店", "スタジオで受付。初めての方でも安心です。", "スタジオ受付"),
        ("instructor-arm-strap.jpg", "stretch", "体験レッスン", "身体の状態に合わせて、インストラクターが丁寧にサポート。", "インストラクターがサポートする体験レッスン"),
        ("flow-consult.jpg", "clipboard", "ご入会", "気に入っていただけたら、そのままスタート。", "タブレットを見ながらプランを相談する手元"),
    ]
    s_html = "".join(
        f'<li class="card step reveal"><span class="step__num">{i + 1:02d}</span>{img(p, alt)}<div class="step__head">{icon(ic)}<h3>{t}</h3></div><p>{d}</p></li>'
        for i, (p, ic, t, d, alt) in enumerate(steps)
    )
    points = [
        ("ring-group-row.jpg", "woman", "女性専用・少人数制", "同じ女性だからこそ、安心して通える空間です。最大6名の少人数制で、一人ひとりに丁寧に向き合います。", "女性専用・少人数制のレッスン"),
        ("studio-akasaka.jpg", "clock", "1回50分", "無理なく続けられるちょうどいいレッスン時間。忙しい方でもライフスタイルに合わせて通えます。", "赤坂店のスタジオ"),
        ("cadillac-arm-support.jpg", "sprout", "初心者歓迎", "運動が苦手な方やピラティスが初めての方も大丈夫。インストラクターがやさしくサポートします。", "初心者をサポートするインストラクター"),
        ("flow-reserve-screen.jpg", "calendar", "予約制", "ご都合に合わせてWEBから予約。予約制なので待ち時間もなく、スムーズにご案内します。", "スマートフォンの予約画面"),
    ]
    p_html = "".join(
        f'<article class="card point reveal">{img(p, alt)}<div class="point__head"><span class="commit__icon">{icon(ic)}</span><h3>{t}</h3></div><p>{d}</p></article>'
        for p, ic, t, d, alt in points
    )
    timeline = [
        ("10分前", "ご来店・受付", "スタジオで受付後、更衣室でお着替えください。"),
        ("50分", "体験レッスン", "リフォーマーを使ったグループレッスン。はじめての方にもわかりやすくご案内します。"),
        ("レッスン後", "ご相談タイム", "続けて通いたい方へ最適なプランをご提案します。無理な勧誘はございません。"),
        ("ご退店", "次回のご案内", "ご入会はオンラインでいつでもお手続きいただけます。"),
    ]
    t_html = "".join(f"<li><b>{a}</b><div><strong>{b}</strong><p>{c}</p></div></li>" for a, b, c in timeline)
    body = f"""{sub_hero("flow", "flow-hero.jpg", "インストラクターのサポートを受けながら体験レッスンを楽しむ女性", "",
        'はじめてでも、<br><span class="pink">迷わず安心。</span>',
        "体験の流れ｜福岡・平尾／赤坂の女性専用ピラティス",
        "体験予約からご入会まで、<br>シンプルな4ステップでご案内します。",
        extra_top=f'<p class="hero__script hero__script--svg">{svg_img("try.svg", "Let’s try Pilates!")}</p>',
        badge="はじめての<br><em>一歩</em>を、<br>私たちが<br>サポートします。")}
<section class="section">
  <div class="container">
    {sec_title("ご入会までの流れ", "たった4ステップで、ピラティスのある新しい毎日が始まります。", "FLOW")}
    <ol class="steps steps--photo" style="list-style:none">{s_html}</ol>
    <p class="center" style="margin-top:40px">{trial_btn("無料体験を予約する", "btn--pink btn--lg")}</p>
  </div>
</section>

<section class="section section--soft">
  <div class="container">
    <div class="sec-title reveal"><span class="sec-title__script sec-title__script--svg" aria-hidden="true">{svg_img("check.svg", "")}</span><h2>はじめての方も安心</h2><p style="font-family:var(--serif);color:var(--navy);font-size:17px">ONE STEPの4つの安心ポイント</p></div>
    <div class="points" style="margin-top:20px">{p_html}</div>
  </div>
</section>

<section class="section section--day">
  <div class="container">
    {sec_title("体験レッスン当日の流れ", "", "TRIAL DAY")}
    <ol class="timeline reveal">{t_html}</ol>
  </div>
</section>

<section class="section section--soft">
  <div class="container">
    {sec_title("持ち物・服装について", "", "WHAT TO BRING")}
    <div class="bring">
      <div class="card reveal">
        <h3>{icon("bag")}レッスンに必要なもの</h3>
        <ul>
          <li>{icon("check")}<span><b>手ぶらでもOK</b><br>上履き・シューズは不要です。</span></li>
          <li>{icon("shirt")}<span>服装は自由です。スカートはご遠慮ください。ジーンズの場合はストレッチ性のあるものがおすすめです。</span></li>
          <li>{icon("sock")}<span>滑り止め付きの靴下があればお持ちください。</span></li>
        </ul>
      </div>
      <div class="card reveal">
        <h3>{icon("sparkle")}あると便利なもの</h3>
        <ul>
          <li>{icon("bottle")}<span>飲み物（ペットボトルなどフタが閉まる容器のもの）</span></li>
          <li>{icon("towel")}<span>汗拭きタオル（ハンカチ程度のもの）</span></li>
          <li>{icon("lock")}<span>更衣室・鍵付きロッカーをご用意しています（シャワー設備はございません）</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>

{cta_band("flow")}"""
    howto_ld = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "PILATES ONE STEPの体験レッスン予約からご入会までの流れ",
        "step": [
            {"@type": "HowToStep", "position": i + 1, "name": t, "text": d.replace("<br>", "")}
            for i, (_, _, t, d, _) in enumerate(steps)
        ],
    }
    page(
        "/flow/",
        "体験の流れ｜はじめてのマシンピラティスも安心｜PILATES ONE STEP（福岡・平尾／赤坂）",
        "PILATES ONE STEPの無料体験レッスンの流れ。WEB予約から来店、50分の体験レッスン、ご入会まで4ステップでご案内。持ち物は手ぶらでOK。平尾・薬院・高宮、赤坂・警固エリアの女性専用ピラティス。",
        body, "/flow/", [howto_ld], og_image="flow-hero.jpg", preload="flow-hero.jpg", head_extra=HAND_FONT,
    )


# ================================================================= FAQ
FAQ = [
    ("trial", "体験レッスンについて", [
        ("初心者でも大丈夫ですか？", "はい。最大6名の少人数制で、インストラクターが一人ひとりに合わせて丁寧にサポートします。運動が苦手な方やピラティスが初めての方も安心してご参加ください。"),
        ("身体が硬くても参加できますか？", "はい。マシンの補助があるため、身体が硬い方でも無理なくご参加いただけます。"),
        ("体験レッスンはどのように予約すればいいですか？", "公式予約サイトより、24時間いつでもお申し込みいただけます。お電話でのご予約は承っておりませんのでご了承ください。詳しくは<a href=\"/flow/\">体験の流れ</a>をご覧ください。"),
        ("体験レッスン当日はどのくらい前に行けばいいですか？", "初回はご説明やお着替えがありますので、レッスン開始時刻の10分前までにお越しください。"),
        ("体験当日の持ち物を教えてください。", "動きやすいウェア、汗拭き用のタオル、お水をご持参ください。シューズは不要です。手ぶらでのご来店も可能です。"),
        ("レッスン時間はどのくらいですか？", "1回50分です。"),
    ]),
    ("reserve", "予約・キャンセルについて", [
        ("レッスンの予約方法を教えてください。", "会員様専用のWEB予約システムからご予約ください。予約がない場合、ご来店いただいてもご受講できませんので、必ず事前にご予約をお願いします。"),
        ("予約のキャンセルはいつまで可能ですか？", "レッスン開始時刻の前日23時59分までにお願いします。それ以降はキャンセル扱いとなります。"),
    ]),
    ("plan", "通い方・プランについて", [
        ("通い放題プランでも予約の制限はありますか？", "通い放題プランでも、一度にお取りいただける予約数には上限がございます。ご受講は1日1回までとなります。詳しくはスタッフまでお尋ねください。"),
        ("平尾店と赤坂店、どちらも利用できますか？", "はい。平尾店・赤坂店の2店舗をご利用いただけます。"),
    ]),
    ("studio", "スタジオ利用について", [
        ("男性も利用できますか？", "当スタジオは女性専用です。男性のご利用はご遠慮いただいております。"),
        ("駐車場や駐輪場はありますか？", "専用の駐車場はございませんので、近隣のコインパーキング等をご利用ください。駐輪場は1Fに駐輪スペースがございます。"),
        ("シャワーやロッカーはありますか？", "更衣室と鍵付きロッカーをご用意しておりますが、シャワー設備はございません。"),
    ]),
    ("other", "その他", [
        ("妊娠中でもレッスンを受けられますか？", "安全のため、妊娠中の方のレッスンはお断りしております。"),
        ("ケガ、または病気をしていますが、レッスンを受けられますか？", "ケガや病気の状況によって、受講いただけない場合があります。医師にご確認いただき、受講前に必ずインストラクターまでお申し出ください。"),
        ("子どもを連れての利用は可能ですか？", "恐れ入りますが、お子さま連れでのご来店はご遠慮ください。"),
    ]),
    ("procedure", "各種お手続きについて", [
        ("入会手続きはどうすればいいですか？", "入会はすべてオンラインで完結します。予約サイトから24時間いつでもお手続きいただけます。店舗での手続きは不要ですので、ご自宅やお好きな場所からスムーズにご入会いただけます。"),
        ("月会費はいつ引き落としになりますか？", "当月の10日締めで、27日に翌月分の月会費を登録口座から引き落としさせていただきます。27日が土日祝日の場合は、翌営業日のお引き落としとなります。クレジットカードの場合、明細への記載時期はカード会社によって異なりますので、ご登録のカード会社へお問い合わせください。"),
        ("プラン変更や解約をするにはどうしたらいいですか？", "変更・解約希望月の2ヶ月前の10日までに、会員証と身分証明書（運転免許証・健康保険証など）をご用意の上、店頭までご来店ください。※10日が定休日の場合は前営業日まで。電話やメール等での変更・解約は承っておりませんので、あらかじめご了承ください。"),
    ]),
]


def strip_tags(s):
    import re
    return re.sub(r"<[^>]+>", "", s)


def build_faq():
    nav = "".join(f'<li><a href="#{k}">{t}</a></li>' for k, t, _ in FAQ)
    groups = []
    for k, t, items in FAQ:
        qs = "".join(
            f'<details class="faq"><summary><span class="qa-mark qa-mark--q" aria-hidden="true">Q</span>{q}{icon("chevdown", "chev")}</summary>'
            f'<div class="faq__a"><span class="qa-mark qa-mark--a" aria-hidden="true">A</span><p>{a}</p></div></details>'
            for q, a in items
        )
        groups.append(f'<section class="faq-group reveal" id="{k}"><h3>{t}</h3>{qs}</section>')
    # 最初の質問は開いた状態で表示
    groups[0] = groups[0].replace('<details class="faq">', '<details class="faq" open>', 2)
    body = f"""{sub_hero("faq", "faq-hero.jpg", "スタジオのテーブルに置かれたノートとハーブティー", "FAQ",
        "よくある質問", "女性専用ピラティス PILATES ONE STEP", "はじめての方から多くいただくご質問を<br>まとめました。")}
<section class="section">
  <div class="container--narrow">
    {sec_title("よくある質問", "", "QUESTIONS")}
    <ul class="faq-nav">{nav}</ul>
    <style>.faq__a a{{color:var(--teal-d);text-decoration:underline}}</style>
    {"".join(groups)}
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <div class="help-band reveal">
      <div class="help-band__body">
        <p>解決しない場合は</p>
        <h2>お気軽にお問い合わせください。</h2>
        <div class="help-band__btns">
          {btn("/contact/", "お問い合わせ", "btn--outline", ico="arrow")}
          {trial_btn("無料体験予約")}
        </div>
      </div>
      {img("instructor-ring-support.jpg", "笑顔で対応するインストラクター")}
    </div>
  </div>
</section>

<section class="section">
  <div class="container">{stores_block(with_title="店舗情報")}</div>
</section>

{cta_band("faq")}"""
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for _, _, items in FAQ for q, a in items
        ],
    }
    page(
        "/faq/",
        "よくある質問｜体験・予約・料金について｜PILATES ONE STEP（福岡・平尾／赤坂）",
        "PILATES ONE STEPのよくある質問。初心者や身体が硬い方の参加、体験レッスンの持ち物、予約・キャンセル、料金のお支払い、駐車場・更衣室など。福岡市中央区 平尾・赤坂の女性専用ピラティス。",
        body, "/faq/", [faq_ld], og_image="faq-hero.jpg", preload="faq-hero.jpg",
    )


# ================================================================= CONTACT
def build_contact():
    store_opts = "".join(f'<option value="{s["name"]}">{s["name"]}</option>' for s in STORES)
    body = f"""{sub_hero("contact", "contact-hero.jpg", "インストラクターと笑顔で会話する女性", "CONTACT",
        "お問い合わせ", "PILATES ONE STEP 平尾店・赤坂店", "ご質問やご相談は、お気軽にお問い合わせください。",
        extra_top=f'<p class="hero__script hero__script--svg">{svg_img("welove.svg", "ピラティスで、もっと好きなわたしに出会える。")}</p>', en_cls="hero__en--teal")}
<section class="section">
  <div class="container contact-grid">
    <div class="card form-card reveal">
      <h2>お問い合わせフォーム</h2>
      <p>ご質問・ご相談など、どんなことでもお気軽にお問い合わせください。スタッフが丁寧に対応いたします。お問い合わせの前に<a href="/faq/" style="color:var(--teal-d);text-decoration:underline">よくある質問</a>もあわせてご確認ください。</p>
      <form class="contact-form" id="form" action="/contact/send.php" method="post">
        <p class="form-msg form-msg--error" style="margin:0 0 22px" hidden role="alert">送信できませんでした。入力内容をご確認のうえ、もう一度お試しください。解決しない場合は<a href="{LINE}" target="_blank" rel="noopener">LINE公式アカウント</a>からお問い合わせください。</p>
        <div class="form-row"><label for="f-name">お名前<span class="req">必須</span></label><input id="f-name" name="name" type="text" autocomplete="name" placeholder="例）山田 花子" required></div>
        <div class="form-row"><label for="f-kana">フリガナ<span class="opt">任意</span></label><input id="f-kana" name="kana" type="text" placeholder="例）ヤマダ ハナコ"></div>
        <div class="form-row"><label for="f-mail">メールアドレス<span class="req">必須</span></label><input id="f-mail" name="email" type="email" autocomplete="email" placeholder="例）example@onestep-p.jp" required></div>
        <div class="form-row"><label for="f-member">会員情報<span class="req">必須</span></label>
          <select id="f-member" name="member" required><option value="">選択してください</option><option>会員</option><option>非会員</option></select></div>
        <div class="form-row"><label for="f-store">ご利用店舗<span class="opt">任意</span></label>
          <select id="f-store" name="store"><option value="">選択してください</option>{store_opts}<option value="未定">未定</option></select></div>
        <div class="form-row"><label for="f-type">お問い合わせ種別<span class="opt">任意</span></label>
          <select id="f-type" name="type"><option value="">選択してください</option><option>体験レッスンについて</option><option>入会・料金について</option><option>レッスン・予約について</option><option>法人のご利用・取材について</option><option>その他</option></select></div>
        <div class="form-row"><label for="f-body">お問い合わせ内容<span class="req">必須</span></label><textarea id="f-body" name="message" placeholder="ご質問・ご相談など、自由にご記入ください" required></textarea></div>
        <p class="form-agree"><label><input type="checkbox" name="agree" value="1" required><a href="/policy/" target="_blank">プライバシーポリシー</a>に同意する</label></p>
        <div style="position:absolute;left:-9999px" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
        <div class="form-submit"><button class="btn btn--pink" type="submit">送信する{icon("arrow")}</button></div>
      </form>
    </div>

    <div>
      <h2 class="side-title reveal">目的に合わせたお問い合わせ</h2>
      <div class="side-cards">
        <div class="side-card side-card--pink reveal">
          <div>
            <div class="side-card__ttl"><span class="circle">{icon("calendar")}</span><h3>無料体験予約</h3></div>
            <p>体験レッスンをご希望の方はこちら</p>
            {btn(TRIAL, "予約する", "btn--pink", ext=True)}
          </div>
          {img("cta-woman.jpg", "体験レッスンを楽しみにする女性")}
        </div>
        <div class="side-card side-card--teal reveal">
          <div>
            <div class="side-card__ttl"><span class="circle">{icon("users")}</span><h3>会員の方の予約・変更</h3></div>
            <p>ご予約や変更はこちらから</p>
            {btn(MEMBER, "会員予約", "btn--teal", ext=True)}
          </div>
          {img("ring-smile.jpg", "レッスンを受ける会員の女性")}
        </div>
        <div class="side-info reveal">
          {icon("clock")}
          <div><h3>営業時間内に順次ご返信いたします</h3><p>通常、3営業日以内にご返信いたします。内容によってはお時間をいただく場合がございます。お急ぎの方はLINE公式アカウントからもお問い合わせいただけます。</p></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--soft">
  <div class="container">{stores_block(with_title="店舗情報")}</div>
</section>

<section class="section">
  <div class="container">
    {sec_title("最新情報はこちらから", "レッスンの様子やお知らせなど、随時発信しています。", "FOLLOW US")}
    <div class="sns-cards">
      <a class="card sns-card sns-card--ig reveal" href="{INSTAGRAM}" target="_blank" rel="noopener"><span class="sns-card__logo">{icon("instagram")}</span><span><h3>Instagram</h3><p>スタジオの雰囲気やレッスンの様子をチェック！</p></span>{icon("arrow", "arrow")}</a>
      <a class="card sns-card sns-card--line reveal" href="{LINE}" target="_blank" rel="noopener"><span class="sns-card__logo">{icon("line")}</span><span><h3>LINE公式アカウント</h3><p>お得な情報やキャンペーンをいち早くお届け！</p></span>{icon("arrow", "arrow")}</a>
    </div>
  </div>
</section>

{cta_band("contact")}"""
    contact_ld = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "name": "お問い合わせ｜PILATES ONE STEP",
        "url": SITE + "/contact/",
        "about": {"@id": SITE + "/#organization"},
    }
    thanks = f"""<section class="hero-mini">
  <img class="branch" src="/assets/img/branch.svg" alt="" aria-hidden="true" style="right:4%;top:-10px;width:130px">
  <div class="container"><p class="hero__en" aria-hidden="true">THANK YOU</p><h1>お問い合わせありがとうございます</h1></div>
</section>
<section class="section section--tight">
  <div class="container--narrow">
    <div class="card legal center reveal">
      <p style="font-family:var(--serif);font-size:18px;color:var(--navy);margin-bottom:18px">お問い合わせを受け付けました。</p>
      <p>ご入力いただいたメールアドレスに、受付完了の自動返信メールをお送りしました。<br>内容を確認のうえ、通常3営業日以内に担当者よりご連絡いたします。</p>
      <p class="note" style="margin-top:14px">※自動返信メールが届かない場合は、迷惑メールフォルダをご確認いただくか、<a href="{LINE}" target="_blank" rel="noopener" style="color:var(--teal-d);text-decoration:underline">LINE公式アカウント</a>からお問い合わせください。</p>
      <div class="help-band__btns" style="margin-top:30px">
        {btn("/", "トップページへ", "btn--outline")}
        {trial_btn("無料体験を予約する")}
      </div>
    </div>
  </div>
</section>
{cta_band("contact")}"""
    page("/contact/thanks/", "お問い合わせ完了｜PILATES ONE STEP", "PILATES ONE STEPへのお問い合わせを受け付けました。",
         thanks, "/contact/", noindex=True)

    page(
        "/contact/",
        "お問い合わせ｜PILATES ONE STEP（福岡・平尾／赤坂の女性専用ピラティス）",
        "PILATES ONE STEPへのお問い合わせはこちら。体験レッスン、入会・料金、レッスン予約などお気軽にご相談ください。平尾店（薬院・高宮エリア）・赤坂店（警固エリア）の女性専用マシンピラティス。",
        body, "/contact/", [contact_ld], og_image="contact-hero.jpg", preload="contact-hero.jpg",
    )


# ================================================================= LEGAL
def legal_page(path, en, title, inner, desc, crumb):
    body = f"""<section class="hero-mini">
  <img class="branch" src="/assets/img/branch.svg" alt="" aria-hidden="true" style="right:4%;top:-10px;width:130px">
  <div class="container"><p class="hero__en" aria-hidden="true">{en}</p><h1>{title}</h1></div>
</section>
<section class="section section--tight">
  <div class="container--narrow"><div class="card legal">{inner}</div></div>
</section>
{cta_band("legal")}"""
    page(path, f"{title}｜PILATES ONE STEP", desc, body, None, [])


def ol(items):
    out = []
    for it in items:
        if isinstance(it, tuple):
            out.append(f"<li>{it[0]}{ol(it[1])}</li>")
        else:
            out.append(f"<li>{it}</li>")
    return "<ol>" + "".join(out) + "</ol>"


def ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def build_legal():
    policy = f"""<p>以下のとおり、当社の提供する本サービス全般における、利用者の個人情報の取扱いについて、プライバシーポリシーを定めます。</p>
<h2>第1条（規約の適用）</h2>
<p>別に定める利用規約に基づく本サービスの利用にあたっての登録手続きは、当社所定の登録フォームにより利用者本人が行うものとします。利用者は登録の際、提示する項目に関して正確な情報を登録するものとします。利用者が登録フォームにおいて必要項目を入力し、登録をした時点で、利用者は本規約の内容に同意したものとします。</p>
<h2>第2条（登録個人情報）</h2>
<p>当社は、利用者が登録し、又は本クラブの運営上当社（委託先を含む）が取得した情報を、個人情報の保護に関する法律その他関係する法律に従い適切に取り扱うとともに、厳重に管理します。当社は、個人情報の取扱いに関する苦情及び相談には、迅速かつ誠実に対応いたします。当社は、利用者が登録した個人情報を次の利用目的の範囲内で利用します。</p>
{ol(["本サービスに関する登録の受付、本人確認、本サービスの提供、維持、保護及び改善のため。", "本サービスに関するご案内、お問合せ等への対応のため。", "本サービスに関する当社の規約、ポリシー等に違反する行為に対する対応のため。", "本サービスに関する規約等の変更などを通知するため。", "上記の利用目的に付随する利用目的のため。", "ダイレクトメール、電子メールを含む各種通知手段によって、当社が有益と判断した企業のさまざま商品情報やサービス情報をお届けするため。", "取得した情報を、分析、集計することで傾向データやマーケティングデータを作成し、商品やサービスの改善等の目的のため。"])}
<p>当社は、事前に利用者本人の承諾を得ることなく個人情報の修正、変更をしないものとします。当社は、法律上の根拠に基づき要求された場合および利用者の同意を得た場合を除き、利用者個人を特定できる個人情報を第三者に開示しないものとします。ただし、当社が業務を委託する委託先に提供する場合がありますので、予めご承諾ください。</p>
<h2>第3条（メールマガジンの配信・配信停止）</h2>
<p>利用者による本サービスの利用登録後、当社は利用者に対して、メールマガジン（メールマガジン関連の情報、告知、運営上の事務連絡に関連する電子メールを含む）を配信できるものとします。メールマガジンには当社の活動等に関する情報のほか、当社又はパートナー等第三者に関する広告、宣伝等が含まれる場合があります。当社は、メールマガジンの配信にあたり、利用者本人が登録した情報のみ使用するものとします。メールマガジンの配信業務を第三者に委託する場合、当社は当該第三者に本プライバシーポリシーの定めを遵守させるものとします。利用者は随時、登録内容の変更又はメールマガジンの配信停止ができるものとします。利用者が登録内容変更又は登録解除を希望する場合、各種通知手段にて当社が記載する方法により、利用者本人が手続きを行うものとします。</p>
<h2>第4条（個人情報の開示）</h2>
<p>当社は、利用者から、個人情報保護法の定めに基づき個人情報の開示を求められたときは、利用者本人からの請求であることを確認の上で、利用者に対し、遅滞なく開示を行います（当該個人情報が存在しないときにはその旨を通知します。）。但し、個人情報保護法その他の法令により、当社が開示の義務を負わない場合は、この限りではありません。</p>
<h2>第5条（個人情報の訂正及び利用停止）</h2>
<p>当社は、利用者から、①個人情報が真実でないという理由によって個人情報保護法の定めに基づきその内容の訂正を求められた場合、及び、②あらかじめ公表された利用目的の範囲を超えて取り扱われているという理由、または偽りその他不正の手段により収集されたものであるという理由により、個人情報保護法の定めに基づき、その利用の停止を求められた場合には、利用者本人からの請求であることを確認の上で遅滞なく必要な調査を行い、その結果に基づき、個人情報の内容の訂正または利用停止を行い、その旨を利用者に通知します。なお、合理的な理由に基づいて訂正または利用停止を行わない旨の決定をしたときは、利用者に対しその旨を通知します。</p>
<h2>第6条（利用者登録解除）</h2>
<p>当社は、以下に該当する場合、利用者の本サービスへの利用登録を事前に通知することなく解除することがあります。</p>
{ol(["利用者が本規約、その他当社が定める各規約に違反した場合", "利用者の登録情報に虚偽、過誤がある場合", "利用者により登録されたメールアドレスが機能していないと判断する場合", "利用者が第三者になりすまして利用登録を行った場合", "利用者本人が登録した情報の利用停止等により配信したメールマガジンが不達となった場合", "利用者により登録されたメールアドレスにつき、第三者から登録した覚えがないのにメールマガジンが届いた等の苦情が届いた場合", "その他、当社が不適当と判断する行為があった場合"])}
<h2>第7条（ウェブサーバーの記録）</h2>
<p>当社のウェブサーバーは、利用者のコンピューターのIPアドレスを自動的に収集・記録しますが、これらは貴方個人を特定するものではありません。利用者自ら個人情報を開示しない限り、利用者は匿名のまま当社ウェブサイトを閲覧することが可能です。</p>
<h2>第8条（準拠法および管轄裁判所）</h2>
<p>本規約の準拠法は日本国法とします。本規約に関する紛争の第一審の専属的合意管轄裁判所は、福岡地方裁判所または福岡簡易裁判所とします。</p>
<h2>第9条（プライバシーポリシーの変更手続）</h2>
<p>当社は、個人情報の取扱いに関する運用状況を適宜見直し、継続的な改善に努めるものとし、必要に応じて、本プライバシーポリシーを変更することがあります。変更した場合には、当社所定の方法で利用者に通知、公表します。</p>
<h2>免責事項</h2>
<p>当社は、以下の事項につき、一切の責任を負わないものとします。</p>
{ul(["本サービスに関する一切の事項についての完全性、正確性、安全性、有用性等", "利用者が本サービスより提供される各種コンテンツ、弊社配信のメールマガジン等によって被った損害", "本サービスに関連して、利用者間で生じたトラブル", "当社ウェブサイトからリンクされた、当社ウェブサイト以外のウェブサイトの内容やサービスに関して生じたトラブル", "利用者が使用するコンピューター、回線、ソフトウェア等の環境等に基づき生じた損害", "本サービスの中断・停止又は本サービスの内容変更によって利用者が受ける損害"])}
<h2>著作権</h2>
{ul(["メールマガジンに掲載される文字、写真、映像、音声等のすべての著作物、肖像、キャラクター、マーク、その他の情報（以下総称して「コンテンツ」という）に関する一切の権利（所有権、知的財産権、肖像権、パブリシティー権等）は、当社もしくは当該権利を有するコンテンツ提供元に帰属します。", "利用者は、コンテンツについて、一切の権利を取得することはないものとし、コンテンツに関する権利を侵害する一切の行為をしてはならないものとします。", "前項の規定に違反して問題が発生した場合、利用者は、自己の費用と責任においてかかる問題を解決するとともに、当社に何らの迷惑又は損害を与えないものとします。"])}
<p class="date">蔵田ビルマネジメント株式会社</p>"""
    legal_page("/policy/", "PRIVACY POLICY", "プライバシーポリシー", policy,
               "PILATES ONE STEP（運営：蔵田ビルマネジメント株式会社）のプライバシーポリシー。個人情報の利用目的、管理、開示・訂正等についてご案内します。", "プライバシーポリシー")

    terms = f"""<p>PILATES ONE STEP（以下、本クラブといいます。）のご利用に際し、下記の事項を厳守されますようご理解・ご協力をお願い申し上げます。</p>
<h2>第1条</h2>
<p>本クラブの運営・管理（会員資格の得喪変更、会費・諸費用の収受、会員規約の制定・改廃等の決定手続きを含む）は蔵田ビルマネジメント株式会社または当社が業務を委託する委託先が行います。</p>
<h2>第2条</h2>
{ol([
    "本クラブに入会できる方は、各要件を満たし、本クラブの趣旨に賛同し本規約を承諾した方について、本クラブが審査の上入会を承認した方とします。",
    ("本クラブの入会資格は、次の項目全てを満たすこととします。", ["各会員種別において別途定める資格を満たすこと。", "本クラブの施設の利用に堪え得る健康状態であることを本クラブに申告いただくこと。", "本規約に同意いただくこと。", "暴力団関係者でないこと。", "刺青（ファッションタトゥーを含みます。）をされていないこと。", "過去に本規約の違反行為をされていないこと。ただし、違反された方であっても、違反事由が解消された場合等で、本クラブが検討した結果、入会資格を認めることがあります。"]),
    "その他本クラブが不適当と認める方は、入会資格がありません。また、入会後であってもこれらの事象が判明した時点で退会していただきます。",
    ("会員は、本クラブに対し、現在のみならず将来にわたって、自らが以下の各号に定める暴力団等の反社会的勢力（以下「反社会的勢力等」といいます。）に該当しないことを保証します。", ["暴力団", "暴力団員（暴力団員でなくなった日から5年を経過しない者を含む）", "暴力団準構成員", "暴力団関係企業の役員、従業員または株主もしくは実質的支配者等の関係者", "その他前各号に準ずるもの"]),
    "会員は、本クラブに対し、反社会的勢力等に対して、直接または間接を問わず、かつ名目の如何を問わず、資金提供を行わないこと、および今後も行う予定がないことを保証します。",
    "会員は、本クラブに対し、反社会的勢力との間で、直接または間接を問わず、社会的に非難されるべき関係のないことを保証します。",
    ("会員は、本クラブに対し、自らまたは第三者を利用して次の各号のいずれの行為も行わないことを保証します。", ["暴力的な要求行為", "法的な責任を超えた不当な要求行為", "取引に関して脅迫的な言動をし、または暴力を用いる行為", "風説を流布し、偽計または威力を用いて本クラブの信用を毀損し、または本クラブの業務を妨害する行為", "その他前各号に準ずる行為"]),
])}
<h2>第3条</h2>
{ol(["本クラブに入会する方は所定の入会手続きを行い、本クラブの承認を得た上、定める会費・入会諸費用をお支払いいただきます。", "必要により医師の健康証明書の提出を求めることがあります。", "入会する本人が未成年者の場合は、本人と保護者の連名で申込み手続きをとらなければなりません。この場合保護者は、自ら会員になった場合と同様に本規約に基づく責任を本人と連帯して負担するものとします。"])}
<h2>第4条</h2>
<p>会員は、本クラブの定める入会金を、所定の方法で本クラブに支払わなければなりません。なお、当該入会金は、入会契約締結及び履行のための必要費用であり、一旦納入した入会金は返還しません。</p>
<h2>第5条</h2>
{ol([("本クラブは、会員が次の各号の一つに該当すると認めた場合は、会員資格の一時停止または除名をすることができます。", ["本クラブの定める会費・諸費用につき、3ヶ月以上滞納したとき。（除名の場合も除名以前の会費・諸費用は全て納入していただきます。）", "本クラブの施設・機材を故意または重過失に毀損したとき。", "本規約、その他本クラブが定める規則その他法令に違反したとき。", "本クラブの名誉や信用を毀損、または秩序を乱したとき。", "入会書類に虚偽を記載したことが判明したとき。", "会員として品位を損なうと認められる非行があったとき。", "伝染病等他人に伝染・感染するおそれのある疾病に罹患したとき。", "医師から運動等を禁じられていることが判明したとき。", "妊娠していることが判明したとき。", "本クラブの合理的な指示・指導に従わないとき。", "その他本クラブが、社会通念に照らし、本クラブ会員としてふさわしくないと認めたとき。"]),
    "前項に基づき本クラブが本規約に基づく契約を解約したことによって会員に損害が生じた場合であっても、本クラブはその損害を賠償する責めを負わないものとします。"])}
<h2>第6条</h2>
<p>会員は、次の行為をしてはいけません。</p>
{ol(["他の会員を含む第三者（以下「他の方」といいます。）や施設スタッフ、本クラブを誹謗、中傷すること。", "他の方や施設スタッフを殴打したり、身体を押したり、拘束する等の暴力行為。", "大声、奇声を発する行為や他の方もしくは施設スタッフの行く手を塞ぐ行為等の威嚇行為または迷惑行為。", "物を投げる、壊す、叩く等、他の方や施設スタッフが恐怖を感じる危険な行為。", "本クラブの施設・器具・備品の損壊や備え付け備品の持ち出し。", "他の方や施設スタッフに対し、待ち伏せし、後をつけ、またはみだりに話しかける等の行為。", "正当な理由なく、面談、電話、その他の方法で施設スタッフに迷惑を及ぼす行為。", "痴漢、のぞき、露出、唾を吐く等、法令や公序良俗に反する行為。", "刃物など危険物の施設への持ち込み。", "施設における物品販売や営業行為、金銭の貸借、勧誘行為、政治活動、署名活動。", "高額な金銭、物の施設への持ち込み。", "本クラブの施設内の秩序を乱す行為。", "自らの会員証を他人に貸与したり、使用させる行為。", "他の会員の会員証を、当該会員の承諾を得たか否かにかかわらず、使用する行為。", "その他、本クラブが会員としてふさわしくないと認める行為。"])}
<h2>第7条</h2>
{ol(["本クラブは、会員が施設に持ち込んだ物を預かりません。会員は、持込物について自己の責任をもって管理するものとします。", "本クラブは、故意または過失がない限り、会員が施設に持ち込んだ物の滅失または毀損について賠償する責任を負いません。",
    ("本クラブは、会員が施設に放置した物に関する一切の権利を放棄したものと見なします。ただし、次の各号に定めるものを除きます。", ["現金及び有価証券", "その価額又はその合計額が一万円以上であると明らかに認められる物", "建物又は自動車の錠を開くことに用いられる鍵、カードキーその他これらに類するもの", "携帯電話用装置", "運転免許証、健康保険の被保険証、在留カードその他法律またはこれに基づく命令の規定により交付された書類であって、個人の地位または個人の一身に専属する権利を証するもの", "預貯金通帳もしくは預貯金の引出用のカード又はクレジットカード", "当該物またはその付属物に記載又は付加した情報により、その所有者または占有者が識別できる物"])])}
<h2>第8条</h2>
{ol(["会員は、本クラブの定める会費等を所定の方法で支払わなければなりません。会費等の種類、金額、支払期限及び支払方法等は本クラブが定めるものとします。", "月会費は、会員が本クラブの会員資格を有する限り、現実に本クラブの施設を利用しない場合も支払い義務が発生します。", "一旦支払われた会費等は、法令の定めまたは本クラブが認める理由がある場合を除き、返還しません。"])}
<h2>第9条</h2>
{ol(["会員は、各月の10日（10日が休館日の場合翌営業日）までに本クラブに所定の休会届を提出することにより、翌月から休会することができます。本クラブの事務手続き上、10日を過ぎた場合は翌々月扱いになります。", "一回の届出による休会期間は1ヶ月から6ヶ月間までとし、休会費は本クラブの定める金額とします。"])}
<h2>第10条</h2>
<p>会員は、各月の10日（10日が休館日の場合翌営業日）までに本クラブに所定の変更届を提出することにより、翌月から会員種類を変更することができます。10日を過ぎた場合は、本クラブの事務手続き上、翌々月扱いになります。</p>
<h2>第11条</h2>
<p>会員は、各月の10日（10日が休館日の場合翌営業日）までに本クラブに所定の退会届を提出することにより、その月末限りで退会することができます。電話等口頭での退会は受け付けません。10日を過ぎた場合は、本クラブの事務手続き上、翌月末日扱いになります。なお、本クラブが退会届を受領しない限り会費支払義務は発生するものとします。</p>
<h2>第12条</h2>
<p>本クラブは、原則として別紙に表記する日を定休日及び季節休業とします。また、その定休日及び季節休業のほか、諸施設の補修、会場整備、その他本クラブの都合により休業することがあります。なお、休業に関してのお知らせは原則として2週間前までに施設内に掲示します。ただし、施設安全管理の面から緊急工事が必要な場合など緊急の事態が発生した場合には、あらかじめ掲示することなく一部または全部の施設を休業することができるものとします。</p>
<h2>第13条</h2>
{ol([("本クラブは、次の事由により本クラブの一部または全部を閉鎖または臨時休業することができます。", ["台風その他異常気象、風水火災害、地震、近隣の事故等で本クラブの業務遂行に支障があるとき。", "施設の改造または補修工事実施のとき。", "法令の制度改廃、行政指導、社会情勢、経済状況の著しい変化があったとき。", "施設の使用権限が消滅する等運営に影響が生ずる事情が発生したとき。", "その他閉鎖または臨時休業の必要があると認められるとき。"]),
    "前項の場合、法令の定めまたは本クラブが認める場合を除き、会員が負担する諸費用の支払義務が軽減され、または免除されることはありません。"])}
<h2>第14条</h2>
{ol(["会員は、自己の責任と危険負担において、他の会員と協調して、本クラブの施設を利用するものとします。", "本クラブは、会員が本クラブの施設利用中に生じた盗難、怪我その他の事故について、本クラブの責めに帰すべき事由がない限り、一切関与せず、責任を負いません。会員同士の本クラブ内外でのトラブルについても同様とします。", "会員は、本クラブにおいて、技量を超えた行為及び危険行為は行ってはならないものとします。また、本クラブの事前の書面による承諾なしに、対価を得て他の利用者に対する指導行為を行ってはならないものとします。"])}
<h2>第15条</h2>
<p>本クラブは、本規約の改定及び変更、及び本規約に基づいて会員が負担すべき諸費用を、社会情勢・経済状況の変動等を参考にして改定することができます。この場合、本クラブは改定日の1ヶ月以上前までに施設内への掲示及び当社ホームページにて会員に告知するものとします。</p>
<h2>第16条</h2>
<p>本規約は2025年7月18日より施行します。</p>"""
    legal_page("/terms/", "TERMS OF USE", "利用規約", terms,
               "PILATES ONE STEPの利用規約。入会資格、会費、休会・退会、施設のご利用についての規約をご案内します。", "利用規約")

    rows = [
        ("販売業者", "蔵田ビルマネジメント株式会社"),
        ("運営統括責任者", "蔵田 崇晴"),
        ("所在地", "〒815-0082 福岡県福岡市南区大楠二丁目12番12号"),
        ("電話番号", "092-600-4556"),
        ("販売価格", "会員種別、商品・サービスごとに異なります。詳細は<a href=\"/price/\" style=\"color:var(--teal-d);text-decoration:underline\">料金ページ</a>に記載しております。"),
        ("商品代金以外に必要な料金", "入会金、消費税"),
        ("引渡し時期", "契約に定めた利用開始日からご利用可能です。"),
        ("返品方法", "サービスの性質上、返品・返金はお受けしておりません。休会・退会の方法は<a href=\"/terms/\" style=\"color:var(--teal-d);text-decoration:underline\">利用規約</a>によります。"),
        ("支払方法", "クレジットカード決済、オンライン口座振替"),
        ("支払時期", "クレジットカード決済：毎月20日に決済<br>オンライン口座振替：毎月27日に引き落とし"),
    ]
    law = '<table class="law-table"><tbody>' + "".join(f"<tr><th scope=\"row\">{a}</th><td>{b}</td></tr>" for a, b in rows) + "</tbody></table>"
    legal_page("/law/", "LEGAL NOTICE", "特定商取引法に基づく表記", law,
               "PILATES ONE STEPの特定商取引法に基づく表記。販売業者、所在地、販売価格、支払方法・時期などをご案内します。", "特定商取引法に基づく表記")


# ================================================================= misc files
def build_misc():
    prio = {"/": "1.0", "/price/": "0.9", "/flow/": "0.9", "/about/": "0.8", "/faq/": "0.8", "/contact/": "0.7", "/news/": "0.7"}
    urls = "".join(
        f"<url><loc>{SITE}{p}</loc><lastmod>{UPDATED}</lastmod><priority>{prio.get(p, '0.5' if p.startswith('/news/') else '0.3')}</priority></url>\n"
        for p in SITEMAP
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html><html lang="ja"><head>
{GTM_HEAD}
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>ページが見つかりません｜{BRAND}</title>{FAVICON_LINKS}
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500&family=Noto+Sans+JP:wght@400;700&family=Noto+Serif+JP:wght@600&display=swap">
<link rel="stylesheet" href="/assets/css/style.css?v={ASSET_VER}">
{GTAG}
</head><body style="padding-top:0">
{GTM_BODY}
<section class="hero-mini" style="min-height:100vh;display:grid;place-items:center;text-align:center"><div class="container">
<p class="hero__en">404</p><h1>お探しのページが見つかりませんでした</h1>
<p style="margin:16px 0 30px">URLが変更されたか、ページが削除された可能性があります。</p>
<a class="btn btn--pink" href="/">トップページへ</a></div></section></body></html>""")


# ================================================================= local preview
PREVIEW = os.path.join(ROOT, "preview")


def build_preview():
    """site/ を複製し、HTMLをダブルクリックで確認できる相対パス版を preview/ に作る。

    site/ は本番用（/about/ のようなきれいなURLのまま）。
    preview/ は確認専用で、リンクを about/index.html のような相対パスに書き換える。
    """
    import re
    import shutil

    if os.path.isdir(PREVIEW):
        shutil.rmtree(PREVIEW)
    shutil.copytree(OUT, PREVIEW)
    attr = re.compile(r'((?:href|src|srcset|action)=")/(?!/)([^"]*)"')
    # 確認用ページの閲覧がアクセス解析に数えられないよう、Googleのタグは外す
    tags = re.compile(r"\n?<!-- Google (?:Tag Manager|tag)[^>]*-->.*?<!-- End Google (?:Tag Manager|tag)[^>]*-->", re.S)
    for dirpath, _, files in os.walk(PREVIEW):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            depth = os.path.relpath(dirpath, PREVIEW).count(os.sep) + (0 if dirpath == PREVIEW else 1)
            prefix = "../" * depth

            def rel(m):
                target = m.group(2)
                base, sep, frag = target.partition("#")
                if base == "" or base.endswith("/"):
                    base += "index.html"
                return f'{m.group(1)}{prefix}{base}{sep}{frag}"'

            with open(path, encoding="utf-8") as f:
                doc = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(attr.sub(rel, tags.sub("", doc)))


if __name__ == "__main__":
    build_photos()
    build_home()
    build_about()
    build_news()
    build_price()
    build_flow()
    build_faq()
    build_contact()
    build_legal()
    build_misc()
    build_preview()
    print(f"built {len(SITEMAP)} pages -> {OUT}")
    print(f"preview (double-click) -> {os.path.join(PREVIEW, 'index.html')}")
