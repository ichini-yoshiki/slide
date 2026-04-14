# =============================================================================
# スライド正本：AI駆動型Webサイト（PPPサイト）自動更新パイプライン
# =============================================================================

---
# ---------------------------------------------------------------------------
# 表紙
# ---------------------------------------------------------------------------
type: cover

html_title: "AI駆動型Webサイト（PPPサイト）自動更新パイプライン"

main_title:
  - "AI駆動型Webサイト（PPPサイト）"
  - "自動更新パイプライン"

sub_title: "～手作業にサヨナラ！AIアシスタントと一緒にサイトを更新しよう～"
meta: "2026年4月 レクチャー担当：ichini"

---
# ---------------------------------------------------------------------------
# 目次
# ---------------------------------------------------------------------------
type: toc

heading: 本日のアジェンダ

items:
  - "はじめに"
  - "PPPサイトAI化の仕組みの共有"
  - "ハンズオン"

---
# ---------------------------------------------------------------------------
# SECTION 1
# ---------------------------------------------------------------------------
type: section

section_num: 1
title: "はじめに"

---
type: bullets

heading: "あらためて、PPPサイトとは？"

items:
  - "自治体と民間企業をつなぐ、ビジネスピッチ（マッチング）サイトです"
  - "参加する首長が増えるのでそのたびにサイトの更新が必要で手間だった"
  - "今回この更新作業をAIで自動化する取り組みをした"
  - html: '<a href="https://pppbusinesspitch.com/" target="_blank" rel="noopener noreferrer">https://pppbusinesspitch.com/</a>'

---
type: bullets

heading: "今日の目標（ゴール）"

items:
  - "PPPサイトがAIで自動更新される仕組みを知る"
  - "実際にPPPサイトを更新できるようになる"

---
# ---------------------------------------------------------------------------
# SECTION 2
# ---------------------------------------------------------------------------
type: section

section_num: 2
title: "PPPサイトAI化の仕組みの共有"

---
type: bullets

heading: "サイトはどうやって更新されるの？（全体像）"

image: img01.png
image_alt: ""

items:
  - "①首長のデータをJSON化（HTMLファイルと切り離しAIリスクを減らす）"
  - "②画像ファイルの命名規則（〇〇県_〇〇市長_いちに太郎に統一）"
  - "③更新のインターフェース（チャットを想定、実装はCursor）"
  - "以上３つのようなアイディアはAI任せではなく人間が主体となり定義すべき。※AI壁打ちはどんどんやるべき"

---
type: bullets

heading: "テストアップと本アップの仕組み（GitHub × Vercel）"

image: img02.png
image_alt: ""

items:
  - "【GitHub】ローカルとバーセルをつなぐ　編集履歴の保存"
  - "【Vercel】今回はテストアップで利用。GitHubへのpushで自動デプロイ"

---
# ---------------------------------------------------------------------------
# SECTION 3
# ---------------------------------------------------------------------------
type: section

section_num: 3
title: "ハンズオン"

---
type: bullets

heading: "PPPサイトを更新できる環境の構築"

items:
  - html: '① <a href="https://github.com/jcossato/ai_ppp" target="_blank" rel="noopener noreferrer">https://github.com/jcossato/ai_ppp</a> をフォークする'
  - html: '② <a href="https://github.com/jcossato/ai_ppp" target="_blank" rel="noopener noreferrer">https://github.com/jcossato/ai_ppp</a>をバーセルに接続する'
  - html: '③ <a href="https://github.com/jcossato/ai_ppp" target="_blank" rel="noopener noreferrer">https://github.com/jcossato/ai_ppp</a>をローカルに落とす'
  - "④ ローカルで首長の更新"
  - html: '⑤ <a href="https://github.com/jcossato/ai_ppp" target="_blank" rel="noopener noreferrer">https://github.com/jcossato/ai_ppp</a>にプッシュする'

---
type: cards

footer_section: "3. まとめ"

heading: "まとめ・Q&A"

cards:
  - "アイディアや構成は人間が主体となり定義する"
  - "バーセルとGitHubでテスト環境を構築する"
  - "【Q&A】気になったこと、分からないことは何でも気軽に聞いてください！"
