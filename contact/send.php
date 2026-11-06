<?php
/**
 * PILATES ONE STEP お問い合わせフォーム送信処理
 *
 * ▼ 公開前に設定してください
 *   MAIL_TO   : お問い合わせを受け取るメールアドレス
 *   MAIL_FROM : 送信元アドレス（サーバーと同じドメインのアドレス推奨。例 no-reply@onestep-p.jp）
 */
const MAIL_TO = 'info@onestep-p.jp';
const MAIL_FROM = 'no-reply@onestep-p.jp';
const FROM_NAME = 'PILATES ONE STEP';
const SITE_HOST = 'onestep-p.jp';

const THANKS_URL = '/contact/thanks/';
const ERROR_URL = '/contact/?error=1#form';

date_default_timezone_set('Asia/Tokyo');
mb_language('Japanese');
mb_internal_encoding('UTF-8');

function back_with_error()
{
    header('Location: ' . ERROR_URL, true, 303);
    exit;
}

// POST以外は受け付けない
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: /contact/', true, 303);
    exit;
}

// 他サイトからの送信を拒否（Origin / Referer がある場合のみ確認）
$src = $_SERVER['HTTP_ORIGIN'] ?? ($_SERVER['HTTP_REFERER'] ?? '');
if ($src !== '') {
    $host = parse_url($src, PHP_URL_HOST);
    $self = preg_replace('/:\d+$/', '', $_SERVER['HTTP_HOST'] ?? '');
    $allowed = [SITE_HOST, 'www.' . SITE_HOST, $self];
    if (!in_array($host, $allowed, true)) {
        back_with_error();
    }
}

// スパム対策（人には見えない入力欄に値が入っていたらボットとみなす）
if (!empty($_POST['website'])) {
    header('Location: ' . THANKS_URL, true, 303);
    exit;
}

function field($key, $max)
{
    $v = isset($_POST[$key]) && is_string($_POST[$key]) ? trim($_POST[$key]) : '';
    $v = str_replace(["\r\n", "\r"], "\n", $v);
    return mb_substr($v, 0, $max);
}

function one_line($v)
{
    // ヘッダーインジェクション防止
    return preg_replace('/[\r\n\t]+/', ' ', $v);
}

$name = one_line(field('name', 60));
$kana = one_line(field('kana', 60));
$email = one_line(field('email', 200));
$member = one_line(field('member', 20));
$store = one_line(field('store', 20));
$type = one_line(field('type', 40));
$message = field('message', 4000);
$agree = !empty($_POST['agree']);

$members = ['会員', '非会員'];
$stores = ['', '平尾店', '赤坂店', '未定'];
$types = ['', '体験レッスンについて', '入会・料金について', 'レッスン・予約について', '法人のご利用・取材について', 'その他'];

if (
    $name === '' || $message === '' || !$agree
    || !filter_var($email, FILTER_VALIDATE_EMAIL)
    || !in_array($member, $members, true)
    || !in_array($store, $stores, true)
    || !in_array($type, $types, true)
) {
    back_with_error();
}

$store_label = $store === '' ? '未選択' : $store;
$kana_label = $kana === '' ? '未記入' : $kana;
$type_label = $type === '' ? '未選択' : $type;
$sent_at = date('Y年n月j日 H:i');

$body = <<<EOT
ホームページのお問い合わせフォームから送信がありました。

■お名前　　　：{$name}
■フリガナ　　：{$kana_label}
■メール　　　：{$email}
■会員情報　　：{$member}
■ご利用店舗　：{$store_label}
■お問い合わせ種別：{$type_label}
■お問い合わせ内容：
{$message}

------------------------------
送信日時：{$sent_at}
EOT;

$from = mb_encode_mimeheader(FROM_NAME) . ' <' . MAIL_FROM . '>';
$params = '-f' . MAIL_FROM;

// 1) スタジオ宛て
$ok = mb_send_mail(
    MAIL_TO,
    '【HPお問い合わせ】' . $type . '（' . $name . '様）',
    $body,
    "From: {$from}\r\nReply-To: {$email}",
    $params
);

if (!$ok) {
    back_with_error();
}

// 2) お客様への自動返信
$reply = <<<EOT
{$name} 様

このたびは PILATES ONE STEP へお問い合わせいただき、
誠にありがとうございます。
以下の内容でお問い合わせを受け付けました。

内容を確認のうえ、通常3営業日以内に担当者よりご連絡いたします。
しばらくお待ちくださいますようお願いいたします。

------------------------------
■お名前　　　：{$name}
■フリガナ　　：{$kana_label}
■会員情報　　：{$member}
■ご利用店舗　：{$store_label}
■お問い合わせ種別：{$type_label}
■お問い合わせ内容：
{$message}
------------------------------

※本メールは送信専用アドレスから自動でお送りしています。
　このメールへのご返信にはお答えできません。
※お心当たりのない場合は、お手数ですが本メールを破棄してください。

無料体験レッスンのご予約はこちら
https://pilates-onestep.hacomono.jp/reserve?trial=true&from=home

==============================
PILATES ONE STEP
女性専用・少人数制マシンピラティス
平尾店：〒810-0015 福岡市中央区那の川2-9-32 ブルク平尾2F
赤坂店：〒810-0042 福岡市中央区赤坂3-11-41 ルネッサンス21赤坂けやき通り 2F
https://onestep-p.jp/
==============================
EOT;

mb_send_mail(
    $email,
    '【PILATES ONE STEP】お問い合わせありがとうございます',
    $reply,
    "From: {$from}",
    $params
);

header('Location: ' . THANKS_URL, true, 303);
exit;
