import streamlit as st
import json
import os
import random
from PIL import Image

# ディレクトリとファイルの定義
DATA_DIR = "mahjong_quiz_data"
IMG_DIR = os.path.join(DATA_DIR, "images")
JSON_PATH = os.path.join(DATA_DIR, "problems.json")

os.makedirs(IMG_DIR, exist_ok=True)

CATEGORIES = [
    "牌効率",
    "押し引き",
    "守備",
    "リーチ判断",
    "鳴き判断",
    "点数計算・役",
    "その他"
]

def load_problems():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_problems(problems):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(problems, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="麻雀 場面復習アプリ", layout="wide")

st.title("🀄 麻雀 場面・牌姿復習アプリ")

# サイドバー：メニューと分野別問題数
st.sidebar.header("📌 メニュー & 統計")
menu = st.sidebar.radio("モード選択", ["問題演習・順次", "ランダム出題", "問題登録", "データ管理・バックアップ"])

problems = load_problems()

# 分野別の問題数カウント
st.sidebar.subheader("📊 分野別登録数")
counts = {cat: 0 for cat in CATEGORIES}
for p in problems:
    cat = p.get("category", "その他")
    if cat in counts:
        counts[cat] += 1

total_count = len(problems)
st.sidebar.text(f"合計登録数: {total_count} 問")
for cat, cnt in counts.items():
    st.sidebar.text(f"- {cat}: {cnt} 問")


# 共通の画像表示関数
def show_image(img_path, caption_text):
    if img_path:
        normalized_path = img_path.replace("/", os.sep).replace("\\", os.sep)
        if os.path.exists(normalized_path):
            try:
                image = Image.open(normalized_path)
                st.image(image, caption=caption_text, use_column_width=True)
            except Exception as e:
                st.error(f"画像の読み込みに失敗しました: {e}")
        else:
            st.warning(f"画像ファイルが見つかりません: {normalized_path}")


# 1. 問題演習・順次モード
if menu == "問題演習・順次":
    st.header("🎯 問題演習（順番通り）")
    
    if not problems:
        st.info("まだ問題が登録されていません。「問題登録」タブから問題を追加してください。")
    else:
        st.subheader("🔍 絞り込み設定")
        selected_categories = st.multiselect(
            "復習する分野を選択してください（未選択の場合はすべて出題）",
            options=CATEGORIES,
            default=[]
        )
        
        filtered_problems = [
            p for p in problems 
            if not selected_categories or p.get("category") in selected_categories
        ]
        
        st.write(f"該当する問題数: **{len(filtered_problems)} 問**")
        
        if filtered_problems:
            if "quiz_index" not in st.session_state:
                st.session_state.quiz_index = 0
                
            if st.session_state.quiz_index >= len(filtered_problems):
                st.session_state.quiz_index = 0
                
            current_p = filtered_problems[st.session_state.quiz_index]
            
            st.divider()
            st.markdown(f"### 問題 {st.session_state.quiz_index + 1} / {len(filtered_problems)}")
            st.markdown(f"**分野:** `{current_p.get('category')}`")
            
            if current_p.get('question_text'):
                st.markdown(f"**状況・メモ:** {current_p.get('question_text')}")
                
            # 牌姿画像
            show_image(current_p.get('image_path'), "牌姿・場面画像")
            
            # 解説の表示切替
            show_answer = st.checkbox("💡 解説を表示する", key=f"ans_seq_{current_p['id']}")
            
            if show_answer:
                st.success(f"**【解説・理由】**\n\n{current_p.get('explanation')}")
                # 解説用画像
                show_image(current_p.get('explanation_image_path'), "解説用画像")
            
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⬅️ 前の問題"):
                    st.session_state.quiz_index = (st.session_state.quiz_index - 1) % len(filtered_problems)
                    st.rerun()
            with col3:
                if st.button("次の問題 ➡️"):
                    st.session_state.quiz_index = (st.session_state.quiz_index + 1) % len(filtered_problems)
                    st.rerun()


# 2. ランダム出題モード
elif menu == "ランダム出題":
    st.header("🎲 ランダム出題モード")
    
    if not problems:
        st.info("まだ問題が登録されていません。「問題登録」タブから問題を追加してください。")
    else:
        st.subheader("🔍 絞り込み設定")
        rand_categories = st.multiselect(
            "出題する分野を選択してください（未選択の場合はすべての分野から出題）",
            options=CATEGORIES,
            default=[],
            key="rand_cat_select"
        )
        
        target_problems = [
            p for p in problems 
            if not rand_categories or p.get("category") in rand_categories
        ]
        
        st.write(f"対象の問題数: **{len(target_problems)} 問**")
        
        if target_problems:
            if "random_list" not in st.session_state or st.session_state.get("last_rand_cats") != rand_categories:
                st.session_state.random_list = random.sample(target_problems, len(target_problems))
                st.session_state.rand_index = 0
                st.session_state.last_rand_cats = rand_categories
                
            if st.session_state.rand_index >= len(st.session_state.random_list):
                st.session_state.rand_index = 0
                
            current_p = st.session_state.random_list[st.session_state.rand_index]
            
            st.divider()
            st.markdown(f"### ランダム出題 ({st.session_state.rand_index + 1} / {len(st.session_state.random_list)})")
            st.markdown(f"**分野:** `{current_p.get('category')}`")
            
            if current_p.get('question_text'):
                st.markdown(f"**状況・メモ:** {current_p.get('question_text')}")
                
            # 牌姿画像
            show_image(current_p.get('image_path'), "牌姿・場面画像")
            
            # 解説の表示切替
            show_answer = st.checkbox("💡 解説を表示する", key=f"ans_rand_{current_p['id']}")
            
            if show_answer:
                st.success(f"**【解説・理由】**\n\n{current_p.get('explanation')}")
                # 解説用画像
                show_image(current_p.get('explanation_image_path'), "解説用画像")
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔀 問題をシャッフルし直す"):
                    st.session_state.random_list = random.sample(target_problems, len(target_problems))
                    st.session_state.rand_index = 0
                    st.rerun()
            with col2:
                if st.button("➡️ 次のランダム問題へ"):
                    st.session_state.rand_index += 1
                    st.rerun()


# 3. 問題登録モード
elif menu == "問題登録":
    st.header("📝 新規問題の登録")
    
    with st.form("registration_form", clear_on_submit=True):
        category = st.selectbox("分野", options=CATEGORIES)
        question_text = st.text_area("状況・条件のメモ（例: 東3局 巡目、点数状況など）")
        uploaded_file = st.file_uploader("牌姿・場面の画像を選択", type=["png", "jpg", "jpeg"], key="q_img")
        explanation = st.text_area("解説・理由（例: 5s外し、安全牌の残し方など）")
        uploaded_exp_file = st.file_uploader("解説用の画像（任意：牌姿の補足や結果の画像など）", type=["png", "jpg", "jpeg"], key="exp_img")
        
        submitted = st.form_submit_button("問題を登録する")
        
        if submitted:
            if not uploaded_file:
                st.warning("メインの牌姿・場面画像をアップロードしてください。")
            else:
                problem_id = str(len(problems) + 1000)
                
                # メイン画像の保存
                img_ext = uploaded_file.name.split(".")[-1]
                img_filename = f"prob_{problem_id}.{img_ext}"
                img_path = os.path.join(IMG_DIR, img_filename)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # 解説用画像の保存（任意）
                exp_img_path = None
                if uploaded_exp_file:
                    exp_ext = uploaded_exp_file.name.split(".")[-1]
                    exp_img_filename = f"exp_{problem_id}.{exp_ext}"
                    exp_img_path = os.path.join(IMG_DIR, exp_img_filename)
                    with open(exp_img_path, "wb") as f:
                        f.write(uploaded_exp_file.getbuffer())
                
                new_problem = {
                    "id": problem_id,
                    "category": category,
                    "question_text": question_text,
                    "image_path": img_path,
                    "explanation": explanation,
                    "explanation_image_path": exp_img_path
                }
                
                problems.append(new_problem)
                save_problems(problems)
                st.success("問題が正常に登録されました！")


# 4. Data Management & Backup Mode
elif menu == "データ管理・バックアップ":
    st.header("💾 データ管理・バックアップ・削除")
    
    st.markdown("""
    - **自動保存:** 登録したデータと画像は、ローカルの `mahjong_quiz_data` フォルダに自動保存されます。
    - **バックアップ:** 現在の全データをJSONファイルとしてダウンロードできます。
    """)
    
    if problems:
        json_str = json.dumps(problems, ensure_ascii=False, indent=2)
        st.download_button(
            label="📥 問題データをJSONとしてダウンロード",
            data=json_str,
            file_name="mahjong_problems_backup.json",
            mime="application/json"
        )
        
        st.divider()
        st.subheader("🗑️ 問題の個別削除")
        st.write("削除したい問題を選択してください。")
        
        # 削除する問題を選ぶセレクトボックスを作成
        problem_options = {f"ID: {p['id']} [{p['category']}] {p.get('question_text', '（メモなし）')[:20]}...": p['id'] for p in problems}
        selected_to_delete_label = st.selectbox("削除する問題", options=list(problem_options.keys()))
        
        if st.button("選択した問題を削除する"):
            target_id = problem_options[selected_to_delete_label]
            # 該当ID以外の問題を残す
            updated_problems = [p for p in problems if p['id'] != target_id]
            save_problems(updated_problems)
            st.success(f"問題（ID: {target_id}）を削除しました！")
            st.rerun()
        
        st.divider()
        st.subheader("⚠️ 全データの削除")
        st.write(f"現在登録されている問題数: {len(problems)}問")
        if st.button("すべてのデータを一括削除する（※注意）"):
            save_problems([])
            st.warning("すべての問題データを削除しました。")
            st.rerun()
    else:
        st.info("管理するデータがありません。")