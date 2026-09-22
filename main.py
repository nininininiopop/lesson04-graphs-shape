import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한 216편의 데이터를 살펴봅니다."
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# ----------------------------------------------------------------------------
# 데이터 불러오기 & 전처리
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # 개봉일(openDt)이 여덟 자리 숫자 형태(YYYYMMDD) -> 날짜형으로 변환
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")

    # genre 열은 세로막대(|) 기호로 여러 장르가 적혀 있을 수 있음 -> 첫 번째 장르만 사용
    df["genre_main"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    return df


with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

st.success(f"총 {len(df)}편의 영화 데이터를 불러왔습니다.")

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ----------------------------------------------------------------------------
st.header("1️⃣ 장르별 영화 편수")

genre_counts = (
    df["genre_main"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="편수")
)

fig_donut = go.Figure(
    data=[
        go.Pie(
            labels=genre_counts["장르"],
            values=genre_counts["편수"],
            hole=0.5,
            hovertemplate="<b>%{label}</b><br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
            textinfo="label+percent",
        )
    ]
)
fig_donut.update_layout(
    title="장르별 영화 편수 비중",
    legend_title="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "장르 도넛 그래프 인사이트",
    placeholder="예) 박스오피스 10위권 영화 중 가장 많이 등장한 장르는 ○○이며, 전체의 약 ○○%를 차지한다.",
    label_visibility="collapsed",
    key="insight_genre_donut",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 2. 장르 안에 영화가 들어 있는 트리맵 - 크기는 총 관객수
# ----------------------------------------------------------------------------
st.header("2️⃣ 장르별 영화 트리맵 (칸 크기 = 총 관객수)")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre_main", "movieNm"],
    values="total_audi",
    title="장르 안에 영화가 들어 있는 트리맵",
)
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "장르-영화 트리맵 인사이트",
    placeholder="예) ○○ 장르 안에서는 <영화명>이 유독 큰 칸을 차지하며, 해당 장르 전체 관객수를 사실상 혼자 견인하고 있다.",
    label_visibility="collapsed",
    key="insight_genre_movie_treemap",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 3. 총 관객수 히스토그램 - 어느 구간에 몰려 있는지 + 최다 관객 영화
# ----------------------------------------------------------------------------
st.header("3️⃣ 총 관객수 히스토그램")

nbins_audi = 30

fig_audi_hist = px.histogram(
    df,
    x="total_audi",
    nbins=nbins_audi,
    title="영화별 총 관객수 히스토그램",
    labels={"total_audi": "총 관객수"},
)
fig_audi_hist.update_traces(hovertemplate="총 관객수 구간: %{x}<br>영화 수: %{y}편<extra></extra>")
fig_audi_hist.update_layout(margin=dict(t=60, b=20, l=20, r=20), yaxis_title="영화 수")

st.plotly_chart(fig_audi_hist, use_container_width=True)

# 가장 영화가 많이 몰려 있는 구간 계산
counts_audi, bin_edges_audi = np.histogram(df["total_audi"], bins=nbins_audi)
top_bin_idx = counts_audi.argmax()
bin_start = bin_edges_audi[top_bin_idx]
bin_end = bin_edges_audi[top_bin_idx + 1]
n_in_top_bin = counts_audi[top_bin_idx]

# 총 관객수가 가장 많은 영화
top_movie_row = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = top_movie_row["total_audi"]

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.info(
    f"전체 216편 중 **{n_in_top_bin}편**의 영화가 총 관객수 "
    f"**{bin_start:,.0f}명 ~ {bin_end:,.0f}명** 구간에 가장 많이 몰려 있습니다. "
    f"총 관객수가 가장 많은 영화는 **'{top_movie_name}'**으로, "
    f"**{top_movie_audi:,.0f}명**을 기록했습니다."
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 4. 개봉일 스크린수 vs 총 관객수 - 산점도 (장르별 색 구분)
# ----------------------------------------------------------------------------
st.header("4️⃣ 개봉일 스크린수와 총 관객수의 관계")

fig_scrn_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "genre_main": "장르",
    },
    title="개봉일 스크린수 vs 총 관객수 (장르별 색 구분)",
)
fig_scrn_scatter.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_scrn_scatter, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "스크린수-관객수 관계 인사이트",
    placeholder="예) 개봉일 스크린수가 많을수록 총 관객수도 대체로 증가하는 양(+)의 관계가 나타난다.",
    label_visibility="collapsed",
    key="insight_scrn_audi_scatter",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 5. 장르별 총 관객수 상자 그림 (영화 10편 이상인 장르만)
# ----------------------------------------------------------------------------
st.header("5️⃣ 장르별 총 관객수 상자 그림")

genre_all_counts = df["genre_main"].value_counts()
genres_10plus = genre_all_counts[genre_all_counts >= 10].index.tolist()
df_genre_10plus = df[df["genre_main"].isin(genres_10plus)]

fig_box = px.box(
    df_genre_10plus,
    x="genre_main",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    points="outliers",
    labels={"genre_main": "장르", "total_audi": "총 관객수"},
    title="영화 10편 이상인 장르별 총 관객수 분포",
)
fig_box.update_layout(margin=dict(t=60, b=20, l=20, r=20), showlegend=False)

st.plotly_chart(fig_box, use_container_width=True)

st.caption(f"영화가 10편 이상인 장르: {', '.join(genres_10plus)}")

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "장르별 상자 그림 인사이트",
    placeholder="예) ○○ 장르는 총 관객수의 중앙값이 가장 높고, △△ 장르는 상자 밖 튀는 영화(이상치)가 많아 흥행 편차가 크다.",
    label_visibility="collapsed",
    key="insight_genre_box",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 6. 버블 그래프 - 개봉일 스크린수 vs 총 관객수 (점 크기 = 개봉 첫주 관객)
# ----------------------------------------------------------------------------
st.header("6️⃣ 개봉일 스크린수와 총 관객수의 관계 (버블: 첫주 관객수)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_main",
    hover_name="movieNm",
    size_max=45,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객수",
        "first_week_audi": "첫주 관객수",
        "genre_main": "장르",
    },
    title="개봉일 스크린수 vs 총 관객수 (점 크기 = 첫주 관객수)",
)
fig_bubble.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "버블 그래프 인사이트",
    placeholder="예) 첫주 관객수가 많았던 영화(큰 점)는 대체로 총 관객수도 많아, 초반 흥행이 최종 흥행으로 이어지는 경향이 있다.",
    label_visibility="collapsed",
    key="insight_bubble_scrn_audi",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 7. 제작 국가 -> 장르 선버스트 (크기 = 영화 편수)
# ----------------------------------------------------------------------------
st.header("7️⃣ 제작 국가 → 장르 선버스트")

fig_sunburst = px.sunburst(
    df,
    path=["nation", "genre_main"],
    title="제작 국가별 장르 구성 (칸 크기 = 영화 편수)",
)
fig_sunburst.update_traces(
    hovertemplate="<b>%{label}</b><br>편수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "국가-장르 선버스트 인사이트",
    placeholder="예) ○○ 국가 영화는 △△ 장르에 집중되어 있는 반면, □□ 국가 영화는 장르가 비교적 고르게 분포되어 있다.",
    label_visibility="collapsed",
    key="insight_nation_genre_sunburst",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 8. 개봉 월별 영화 편수 분포
# ----------------------------------------------------------------------------
st.header("8️⃣ 개봉 월별 영화 편수 분포")

df_month = df.dropna(subset=["openDt"]).copy()
df_month["open_month"] = df_month["openDt"].dt.month

month_counts = (
    df_month["open_month"]
    .value_counts()
    .reindex(range(1, 13), fill_value=0)
    .rename_axis("월")
    .reset_index(name="편수")
)
month_counts["월"] = month_counts["월"].apply(lambda m: f"{m}월")

fig_month = px.bar(
    month_counts,
    x="월",
    y="편수",
    text="편수",
    title="개봉 월별 영화 편수",
)
fig_month.update_traces(hovertemplate="개봉월: %{x}<br>편수: %{y}편<extra></extra>")
fig_month.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_month, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "개봉 월별 편수 인사이트",
    placeholder="예) 박스오피스 10위권에 든 영화는 ○○월에 가장 많이 개봉했으며, 방학·연휴가 낀 달에 개봉작이 몰리는 경향이 있다.",
    label_visibility="collapsed",
    key="insight_open_month_bar",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 9. 제작 국가별 영화 편수 - 막대 그래프 (분포)
# ----------------------------------------------------------------------------
st.header("9️⃣ 제작 국가별 영화 편수")

nation_counts = (
    df["nation"]
    .value_counts()
    .rename_axis("국가")
    .reset_index(name="편수")
)

fig_nation = px.bar(
    nation_counts,
    x="국가",
    y="편수",
    text="편수",
    title="제작 국가별 영화 편수",
)
fig_nation.update_traces(hovertemplate="국가: %{x}<br>편수: %{y}편<extra></extra>")
fig_nation.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_nation, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "국가별 편수 인사이트",
    placeholder="예) 박스오피스 10위권에 든 영화의 제작 국가는 ○○이 가장 많으며, 국내외 영화 비중은 대략 ○○ 정도이다.",
    label_visibility="collapsed",
    key="insight_nation_bar",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 10. 총 관객수 분포 - 히스토그램 (분포)
# ----------------------------------------------------------------------------
st.header("🔟 총 관객수 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객수 분포",
    labels={"total_audi": "총 관객수"},
)
fig_hist.update_traces(hovertemplate="총 관객수 구간: %{x}<br>영화 수: %{y}편<extra></extra>")
fig_hist.update_layout(margin=dict(t=60, b=20, l=20, r=20), yaxis_title="영화 수")

st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "총 관객수 분포 인사이트",
    placeholder="예) 대다수의 영화는 총 관객수가 ○○명 이하에 몰려 있고, 일부 영화만 대규모 흥행을 기록했다.",
    label_visibility="collapsed",
    key="insight_audi_hist",
)

st.divider()


# ----------------------------------------------------------------------------
# 그래프 11. 10위권 유지 일수와 총 관객수의 관계 - 산점도 (관계)
# ----------------------------------------------------------------------------
st.header("1️⃣1️⃣ 박스오피스 10위권 유지 일수와 총 관객수의 관계")

fig_scatter2 = px.scatter(
    df,
    x="days_in_top10",
    y="total_audi",
    color="genre_main",
    hover_name="movieNm",
    labels={
        "days_in_top10": "10위권 유지 일수",
        "total_audi": "총 관객수",
        "genre_main": "장르",
    },
    title="10위권 유지 일수 vs 총 관객수",
)
fig_scatter2.update_layout(margin=dict(t=60, b=20, l=20, r=20))

st.plotly_chart(fig_scatter2, use_container_width=True)

st.markdown("**📌 이 그래프로 알 수 있는 것**")
st.text_area(
    "유지 일수-관객수 관계 인사이트",
    placeholder="예) 10위권에 오래 머문 영화일수록 총 관객수가 많은 경향이 있으나, 예외적으로 짧게 머물고도 큰 흥행을 한 영화도 존재한다.",
    label_visibility="collapsed",
    key="insight_days_audi_scatter",
)

st.divider()
st.caption("데이터 출처: https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv")
