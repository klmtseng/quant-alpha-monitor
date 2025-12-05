import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime

# --- 1. 網頁基本設定 (必須放在第一行) ---
st.set_page_config(
    page_title="Quant Alpha Monitor",
    page_icon="📈",
    layout="wide"
)

# --- 2. 核心功能：抓取 arXiv 資料 ---
# 使用快取 (TTL=3600秒/1小時)，避免每次重新整理都向 arXiv 請求，加快速度
@st.cache_data(ttl=3600)
def fetch_arxiv_data():
    # arXiv API 查詢：分類為 Quantitative Finance (q-fin)，依日期排序
    RSS_URL = 'http://export.arxiv.org/api/query?search_query=cat:q-fin.*&start=0&max_results=20&sortBy=submittedDate&sortOrder=descending'
    
    try:
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            return None

        papers = []
        for entry in feed.entries:
            # 整理每篇論文的資訊
            papers.append({
                '發布日期': entry.published[:10],
                '標題': entry.title.replace('\n', ' '),
                '摘要': entry.summary.replace('\n', ' '),
                '連結': entry.link,
                '作者': ', '.join([author.name for author in entry.authors])
            })
        
        return pd.DataFrame(papers)
    except Exception as e:
        st.error(f"連線發生錯誤: {e}")
        return None

# --- 3. 側邊欄設計 (個人品牌區) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1086/1086741.png", width=100) # 示意圖示
    st.header("👨‍💻 關於作者")
    st.markdown("""
    **您的名字/ID** *Quantitative Researcher*
    
    專注領域：
    * 🚀 Momentum 動能策略
    * 📊 計量經濟模型
    * 🤖 演算法交易
    """)
    
    st.info("ℹ️ 本專案展示自動化資料搜集與市場監控能力。")
    st.markdown("---")
    st.caption("Data Source: arXiv API")

# --- 4. 主頁面內容 ---
st.title("📈 Quant Alpha Monitor | 量化策略實驗室")
st.markdown("### 全球最新計量金融 (Quantitative Finance) 論文快訊")
st.write(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
st.markdown("---")

# --- 5. 顯示資料 ---
df_papers = fetch_arxiv_data()

if df_papers is not None and not df_papers.empty:
    # 統計數據
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="今日抓取論文數", value=len(df_papers))
    with col2:
        st.metric(label="監控分類", value="q-fin (Quantitative Finance)")

    st.markdown("#### 📄 最新論文列表")
    
    # 用卡片式 (Expander) 呈現，比較整潔
    for index, row in df_papers.iterrows():
        # 標題格式：[日期] 論文題目
        card_title = f"🗓️ {row['發布日期']} | {row['標題']}"
        
        with st.expander(card_title):
            st.markdown(f"**👨‍🏫 作者:** {row['作者']}")
            st.markdown(f"**📝 摘要:** {row['摘要']}")
            st.markdown(f"[🔗 閱讀完整論文 ({row['連結']})]({row['連結']})")
            
else:
    st.warning("目前無法取得資料，請稍後再試。")