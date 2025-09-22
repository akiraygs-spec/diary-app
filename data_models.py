import datetime
from dataclasses import dataclass

# Define data models
@dataclass
class Goal:
    id: str
    title: str
    description: str
    category: str
    deadline: str
    created_date: str
    user_email: str = ""

@dataclass
class User:
    email: str
    password_hash: str
    nickname: str
    created_date: str

@dataclass
class DiaryEntry:
    date: str
    title: str
    content: str
    mood: str
    mood_intensity: int
    category: str
    user_email: str = ""
    bot_response: str = ""

# Define constants for themes, moods, and tips
THEME_PALETTES = {
    "ソフトブルー": {
        "primary": "#87ceeb", "secondary": "#add8e6", "accent": "#e0f6ff",
        "background": "#f8fcff", "surface": "#f5faff", "card": "rgba(245, 250, 255, 0.9)",
        "text_primary": "#4682b4", "text_secondary": "#6495ed", "border": "rgba(135, 206, 235, 0.3)",
        "shadow": "rgba(135, 206, 235, 0.2)", "gradient": "linear-gradient(135deg, #f8fcff 0%, #e0f6ff 100%)"
    },
    "パステルピンク": {
        "primary": "#ffc0cb", "secondary": "#ffb6c1", "accent": "#ffe4e6",
        "background": "#fffafc", "surface": "#fff5f8", "card": "rgba(255, 245, 248, 0.9)",
        "text_primary": "#cd919e", "text_secondary": "#db7093", "border": "rgba(255, 192, 203, 0.3)",
        "shadow": "rgba(255, 192, 203, 0.2)", "gradient": "linear-gradient(135deg, #fffafc 0%, #ffe4e6 100%)"
    },
    "ミントグリーン": {
        "primary": "#98fb98", "secondary": "#90ee90", "accent": "#f0fff0",
        "background": "#f8fff8", "surface": "#f5fff5", "card": "rgba(245, 255, 245, 0.9)",
        "text_primary": "#228b22", "text_secondary": "#32cd32", "border": "rgba(152, 251, 152, 0.3)",
        "shadow": "rgba(152, 251, 152, 0.2)", "gradient": "linear-gradient(135deg, #f8fff8 0%, #f0fff0 100%)"
    },
    "ラベンダーミスト": {
        "primary": "#e6e6fa", "secondary": "#dda0dd", "accent": "#f8f8ff",
        "background": "#fefcff", "surface": "#faf8ff", "card": "rgba(250, 248, 255, 0.9)",
        "text_primary": "#9370db", "text_secondary": "#ba55d3", "border": "rgba(230, 230, 250, 0.4)",
        "shadow": "rgba(230, 230, 250, 0.2)", "gradient": "linear-gradient(135deg, #fefcff 0%, #f8f8ff 100%)"
    },
    "ピーチクリーム": {
        "primary": "#ffdab9", "secondary": "#ffe4b5", "accent": "#fff8dc",
        "background": "#fffefa", "surface": "#fffcf5", "card": "rgba(255, 252, 245, 0.9)",
        "text_primary": "#cd853f", "text_secondary": "#daa520", "border": "rgba(255, 218, 185, 0.3)",
        "shadow": "rgba(255, 218, 185, 0.2)", "gradient": "linear-gradient(135deg, #fffefa 0%, #fff8dc 100%)"
    },
    "クラウドグレー": {
        "primary": "#d3d3d3", "secondary": "#dcdcdc", "accent": "#f8f8ff",
        "background": "#fafafa", "surface": "#f7f7f7", "card": "rgba(247, 247, 247, 0.9)",
        "text_primary": "#696969", "text_secondary": "#808080", "border": "rgba(211, 211, 211, 0.4)",
        "shadow": "rgba(211, 211, 211, 0.2)", "gradient": "linear-gradient(135deg, #fafafa 0%, #f8f8ff 100%)"
    }
}

MOOD_OPTIONS = {
    "ポジティブ": [
        {"name": "喜び", "color": "#87ceeb", "intensity": 5},
        {"name": "面白い", "color": "#87ceeb", "intensity": 5},
        {"name": "満足", "color": "#87ceeb", "intensity": 4},
        {"name": "ワクワク", "color": "#87ceeb", "intensity": 4}
    ],
    "穏やか": [
        {"name": "安心", "color": "#98fb98", "intensity": 4},
        {"name": "穏やか", "color": "#98fb98", "intensity": 3},
        {"name": "ドキドキ", "color": "#98fb98", "intensity": 3},
        {"name": "感謝", "color": "#98fb98", "intensity": 4}
    ],
    "ニュートラル": [
        {"name": "普通", "color": "#d3d3d3", "intensity": 2},
        {"name": "退屈", "color": "#d3d3d3", "intensity": 2},
        {"name": "疲れた", "color": "#d3d3d3", "intensity": 1},
        {"name": "モヤモヤ", "color": "#d3d3d3", "intensity": 1}
    ],
    "不安・心配": [
        {"name": "不安", "color": "#ffdab9", "intensity": 1},
        {"name": "緊張", "color": "#ffdab9", "intensity": 1},
        {"name": "後悔", "color": "#ffdab9", "intensity": 2},
        {"name": "孤独", "color": "#ffdab9", "intensity": 1}
    ],
    "ネガティブ": [
        {"name": "悲しみ", "color": "#ffc0cb", "intensity": 1},
        {"name": "イライラ", "color": "#ffc0cb", "intensity": 1},
        {"name": "怒り", "color": "#ffc0cb", "intensity": 0},
        {"name": "絶望", "color": "#ffc0cb", "intensity": 0}
    ]
}

ACHIEVEMENT_TIPS = {
    "習慣化のコツ": [
        {"title": "小さく始める", "content": "大きな目標も小さな習慣から。1日1ページの読書、5分の運動など、必ず継続できる小さなことから始めましょう。"},
        {"title": "環境を整える", "content": "習慣化したい行動がしやすい環境を作りましょう。本を読みたいなら手の届く場所に本を置く、運動したいなら運動着を見えるところに置く。"},
        {"title": "きっかけを作る", "content": "既存の習慣に新しい習慣を紐づけることで継続しやすくなります。「歯磨きの後に読書」「コーヒーを飲んだら日記」など。"},
        {"title": "記録を取る", "content": "進歩を可視化することで達成感を得られます。カレンダーにチェックを付ける、アプリで記録するなど、自分に合った方法で。"}
    ],
    "モチベーション管理": [
        {"title": "なぜその目標なのかを明確に", "content": "目標を設定した理由を深く考えてみましょう。「なぜ英語を学びたいのか」「なぜ健康でいたいのか」理由が明確だと継続しやすくなります。"},
        {"title": "進歩を祝う", "content": "小さな成果も積極的に祝いましょう。1週間続けたら好きなケーキを食べる、1ヶ月達成したら映画を見るなど。"},
        {"title": "完璧を求めすぎない", "content": "1日サボったからといって諦めないこと。完璧な人はいません。大切なのは再び始めることです。"},
        {"title": "仲間を見つける", "content": "同じ目標を持つ仲間や、あなたを応援してくれる人を見つけましょう。一人では難しいことも、支え合えば継続できます。"}
    ],
    "時間管理": [
        {"title": "優先順位を決める", "content": "すべてを同時にやろうとせず、最も重要な1-3つの目標に集中しましょう。エネルギーを分散させず集中することが成功の鍵です。"},
        {"title": "スケジュールに組み込む", "content": "目標達成のための時間を具体的にスケジュールに組み込みましょう。「いつかやる」ではなく「毎日7時から」など具体的に。"},
        {"title": "デッドタイムを活用", "content": "通勤時間、待ち時間、入浴時間などの隙間時間を有効活用しましょう。英語の音声を聞く、読書をするなど。"},
        {"title": "エネルギー管理", "content": "自分が最もエネルギーの高い時間帯を把握し、重要なタスクをその時間に配置しましょう。朝型？夜型？自分を知ることから。"}
    ],
    "メンタルヘルス": [
        {"title": "セルフコンパッション", "content": "自分に優しくしましょう。失敗や挫折があっても自分を責めず、友人に接するように自分にも優しい言葉をかけてあげてください。"},
        {"title": "感情を受け入れる", "content": "やる気が出ない日、落ち込む日があるのは自然なこと。そんな感情も受け入れつつ、できることを少しずつやってみましょう。"},
        {"title": "リラックスタイムを確保", "content": "頑張ることも大切ですが、リラックスする時間も同様に重要です。散歩、瞑想、音楽鑑賞など、心を休める時間を作りましょう。"},
        {"title": "成長マインドセット", "content": "「できない」ではなく「まだできない」と考えましょう。能力は努力によって伸ばすことができるという信念を持つことが大切です。"}
    ]
}