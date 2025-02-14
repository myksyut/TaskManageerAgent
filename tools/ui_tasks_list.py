import streamlit as st
import yaml
from datetime import datetime
import pandas as pd
from pathlib import Path

def load_tasks():
    tasks_file = Path(__file__).parent.parent / "data" / "tasks.yaml"
    with open(tasks_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["tasks"]

def save_tasks(tasks):
    tasks_file = Path(__file__).parent.parent / "data" / "tasks.yaml"
    with open(tasks_file, "w", encoding="utf-8") as f:
        yaml.dump({"tasks": tasks}, f, allow_unicode=True)

def display_tasks():
    st.title("🗓️ タスク管理ボード")
    
    # セッション状態の初期化
    if 'show_completion' not in st.session_state:
        st.session_state.show_completion = False
        st.session_state.completed_task = None
    
    # 完了メッセージの表示
    if st.session_state.show_completion:
        st.balloons()
        st.success(f"🎉 おめでとうございます！タスク「{st.session_state.completed_task}」が完了しました！")
        st.session_state.show_completion = False
    
    tasks = load_tasks()
    
    # 定数定義
    TASK_STATUSES = ["未着手", "進行中", "保留", "完了"]
    MAX_PRIORITY = 5
    
    # サイドバーにフィルターを配置
    with st.sidebar:
        st.header("フィルター設定")
        filter_status = st.multiselect(
            "ステータス:",
            TASK_STATUSES,
            default=["未着手", "進行中"]
        )
        
        priority_filter = st.slider(
            "優先度（最小値）:",
            min_value=1,
            max_value=MAX_PRIORITY,
            value=1
        )
        
        sort_by = st.selectbox(
            "ソート順:",
            ["優先度", "期限", "作成日"],
            index=0
        )
        
        sort_order = st.radio(
            "ソート方向:",
            ["降順", "昇順"],
            horizontal=True
        )
        
        apply_filter = st.button("フィルターを適用", type="primary")
        
        if st.button("フィルターをリセット"):
            filter_status = TASK_STATUSES
            priority_filter = 1
            sort_by = "優先度"
            sort_order = "降順"
            st.rerun()

    # タスクをDataFrameに変換して操作しやすくする
    df = pd.DataFrame(tasks)
    
    # フィルターとソートの適用
    if apply_filter:
        # ステータスでフィルター
        filtered_tasks = [task for task in tasks if task["status"] in filter_status]
        # 優先度でフィルター
        filtered_tasks = [task for task in filtered_tasks if task["priority"] >= priority_filter]
        
        # ソート
        if sort_by == "優先度":
            filtered_tasks = sorted(filtered_tasks, 
                                 key=lambda x: x["priority"],
                                 reverse=(sort_order == "降順"))
        elif sort_by == "期限":
            filtered_tasks = sorted(filtered_tasks,
                                 key=lambda x: x["due_date"],
                                 reverse=(sort_order == "降順"))
        else:  # 作成日
            filtered_tasks = sorted(filtered_tasks,
                                 key=lambda x: x["created_at"],
                                 reverse=(sort_order == "降順"))
    else:
        filtered_tasks = tasks

    # タスク数の表示
    st.markdown(f"### 表示中のタスク: {len(filtered_tasks)}件")
    
    for task in filtered_tasks:
        with st.container():
            # ヘッダー部分
            col1, col2, col3 = st.columns([6, 2, 2])
            with col1:
                st.header(task['title'])
            with col2:
                st.markdown(f"**優先度**: {'🔥' * task['priority']}")
            with col3:
                status_colors = {
                    "未着手": "🔵",
                    "進行中": "🟡",
                    "保留": "⚪",
                    "完了": "🟢"
                }
                current_status = task["status"]
                st.markdown(f"**ステータス**: {status_colors[current_status]} {current_status}")
                new_status = st.selectbox(
                    "変更",
                    TASK_STATUSES,
                    index=TASK_STATUSES.index(current_status),
                    key=f"status_{task['id']}"
                )
                
                # ステータスが変更された場合、保存
                if new_status != current_status:
                    # 完了状態に変更された場合、セッション状態を更新
                    if new_status == "完了" and current_status != "完了":
                        st.session_state.show_completion = True
                        st.session_state.completed_task = task['title']
                    task["status"] = new_status
                    save_tasks(tasks)
                    st.rerun()
            
            # タスクの詳細情報
            st.markdown(f"**カテゴリ**: {task['category']}")
            st.markdown(f"**期限**: {task['due_date'].split('T')[0]}")
            st.markdown(f"**予定工数**: {task['estimated_hours']}時間")
            
            # 説明文
            with st.expander("詳細を表示"):
                st.markdown(task["description"])
            
            st.divider()

if __name__ == "__main__":
    st.set_page_config(
        page_title="タスク管理ボード",
        page_icon="📋",
        layout="wide"
    )
    display_tasks()
