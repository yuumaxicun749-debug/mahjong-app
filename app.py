import streamlit as st
import json
import os
import random
from PIL import Image

# ディレクトリとファイルの定義
DATA_DIR = "mahjong_quiz_data"
IMG_DIR = os.path.join(DATA_DIR, "images")
JSON_PATH = os.path.join(DATA_DIR, "problems.json")
CATEGORIES_PATH = os.path.join(DATA_DIR, "categories.json")

os.makedirs(IMG_DIR, exist_ok=True)

# デフォルトの分野リスト
DEFAULT_CATEGORIES = [
    "牌効率",
    "押し引き",
    "守備",
    "リーチ判断",
    "鳴き判断",
    "点数計算・役",
    "その他"
]

def load_categories():
    if os.path.exists(CATEGORIES_PATH):
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CATEGORIES

def save_categories(categories):
    with open(CATEGORIES_PATH, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)

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

# データの読み込み
categories = load_categories()
problems = load_problems()

# サイドバー：メニューと分野別問題数
st.sidebar.header("📌 メニュー & 統計")
menu = st.sidebar.radio("モード選択", ["問題演習・順次", "ランダム出題", "問題登録", "分野管理", "データ管理・バックアップ"])

# 分野別の問題数カウント
st.sidebar.subheader("📊 分野別登録数")
counts = {cat: 0 for cat in categories}
for p in problems:
    cat = p.get("category", "その他")
    if cat in counts:
        counts[cat] += 1
    else:
        # 存在しないカテゴリの場合は「その他」などに寄せる、またはそのままカウント
        if "その他" in counts:
            counts["その他"] += 1

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
            options=categories,
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
                
            show_image(current_p.get('image_path'), "牌姿・場面画像")
            
            show_answer = st.checkbox("💡 解説を表示する", key=f"ans_seq_{current_p['id']}")
            
            if show_answer:
                st.success(f"**【解説・理由】**\n\n{current_p.get('explanation')}")
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
            options=categories,
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
                
            show_image(current_p.get('image_path'), "牌姿・場面画像")
            
            show_answer = st.checkbox("💡 解説を表示する", key=f"ans_rand_{current_p['id']}")
            
            if show_answer:
                st.success(f"**【解説・理由】**\n\n{current_p.get('explanation')}")
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
        category = st.selectbox("分野", options=categories)
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
                
                img_ext = uploaded_file.name.split(".")[-1]
                img_filename = f"prob_{problem_id}.{img_ext}"
                img_path = os.path.join(IMG_DIR, img_filename)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
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


# 4. 分野管理モード
elif menu == "分野管理":
    st.header("🏷️ 分野（カテゴリ）の管理")
    
    st.markdown("現在登録されている分野の追加・編集・削除が行えます。")
    
    # 新規分野の追加
    st.subheader("➕ 新規分野の追加")
    new_cat_name = st.text_input("追加する分野名を入力")
    if st.button("分野を追加"):
        if new_cat_name.strip() and new_cat_name not in categories:
            categories.append(new_cat_name.strip())
            save_categories(categories)
            st.success(f"分野「{new_cat_name}」を追加しました！")
            st.rerun()
        elif new_cat_name in categories:
            st.warning("その分野はすでに存在します。")
        else:
            st.warning("有効な分野名を入力してください。")

    st.divider()
    st.subheader("✏️ 既存分野の編集・削除")
    
    if categories:
        selected_cat = st.selectbox("管理する分野を選択", options=categories)
        
        col1, col2 = st.columns(2)
        with col1:
            renamed_cat = st.text_input("分野名を変更する場合の新しい名前", value=selected_cat)
            if st.button("分野名を更新"):
                if renamed_cat.strip() and renamed_cat not in categories:
                    old_name = selected_cat
                    # カテゴリリストの更新
                    idx = categories.index(old_name)
                    categories[idx] = renamed_cat.strip()
                    save_categories(categories)
                    
                    # 登録されている問題のカテゴリ名も一括で書き換える
                    for p in problems:
                        if p.get("category") == old_name:
                            p["category"] = renamed_cat.strip()
                    save_problems(problems)
                    
                    st.success(f"分野名を「{old_name}」から「{renamed_cat}」に変更しました！")
                    st.rerun()
                elif renamed_cat in categories:
                    st.warning("その名前の分野はすでに存在します。")
                else:
                    st.warning("有効な名前を入力してください。")
                    
        with col2:
            st.write("")
            st.write("")
            if len(categories) > 1:
                if st.button("選択した分野を削除"):
                    # 削除されたカテゴリに属していた問題はどうするか（例: 「その他」に変更）
                    categories.remove(selected_cat)
                    save_categories(categories)
                    
                    for p in problems:
                        if p.get("category") == selected_cat:
                            p["category"] = "その他"  # デフォルトへ逃がす
                    save_problems(problems)
                    
                    st.success(f"分野「{selected_cat}」を削除しました（該当問題は「その他」に移動しました）！")
                    st.rerun()
            else:
                st.warning("すべての分野を削除することはできません。")
    else:
        st.info("登録されている分野がありません。")


# 5. データ管理・バックアップモード
elif menu == "データ管理・バックアップ":
    st.header("💾 データ管理・バックアップ・削除")
    
    st.markdown("""
    - **自動保存:** 登録したデータや分野、画像は、ローカルの `mahjong_quiz_data` フォルダに自動保存されます。
    - **バックアップ:** 現在の全問題データをJSONファイルとしてダウンロードできます。
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
        problem_options = {f"ID: {p['id']} [{p['category']}] {p.get('question_text', '（メモなし）')[:20]}...": p['id'] for p in problems}
        selected_to_delete_label = st.selectbox("削除する問題", options=list(problem_options.keys()))
        
        if st.button("選択した問題を削除する"):
            target_id = problem_options[selected_to_delete_label]
            updated_problems = [p for p in problems if p['id'] != target_id]
            save_problems(updated_problems)
            st.success(f"問題（ID: {target_id}）を削除しました！")
            st.rerun()
        
        st.divider()
        st.subheader("⚠️ 全データの削除")
        st.write(f"現在登録されている問題数: {len(problems)}問")
        if st.button("すべての問題を一括削除する（※注意）"):
            save_problems([])
            st.warning("すべての問題データを削除しました。")
            st.rerun()
    else:
        st.info("管理する問題データがありません。")
