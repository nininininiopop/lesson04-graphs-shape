import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------
# 기본 설정
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
    최근 1년간 박스오피스 10위권에 든 영화 가운데, 이 기간에 개봉한
    **216편**의 정보를 담은 데이터를 활용합니다.
    """
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# -----------------------------------------------------------------------
# 데이터 불러오기 & 전처리
# -----------------------------------------------------------------------
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)

    # genre 열에 세로막대(|) 기호로 여러 장르가 적혀 있는 경우, 첫 번째 장르만 사용
    if "genre" in df.columns:
        df["genre"] = (
            df["genre"]
            .astype(str)
            .apply(lambda x: x.split("|")[0].strip())
        )

    # openDt(개봉일, 8자리 숫자)를 날짜 타입으로 변환
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    return df


with st.spinner("데이터를 불러오는 중입니다..."):
    df = load_data(DATA_URL)

with st.expander("원본 데이터 미리보기"):
    st.dataframe(df, use_container_width=True)

st.divider()


# -----------------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# -----------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_genre.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)
fig_genre.update_layout(
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="장르별 영화 편수 그래프 해석",
    value="",
    placeholder="예: 최근 1년간 박스오피스 10위권에 가장 많이 오른 장르는 ○○이며, 전체의 약 ○○%를 차지한다.",
    label_visibility="collapsed",
    key="insight_genre_donut",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 2. 장르 안에 영화가 들어 있는 트리맵 (칸 크기 = 총 관객)
# -----------------------------------------------------------------------
st.header("2. 장르별 영화 트리맵 (칸 크기 = 총 관객)")

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), "genre", "movieNm"],
    values="total_audi",
)
fig_treemap.update_traces(
    hovertemplate="영화명: %{label}<br>총 관객: %{value:,}명<extra></extra>",
)
fig_treemap.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="장르별 영화 트리맵 해석",
    value="",
    placeholder="예: ○○ 장르 안에서는 <영화명>이 총 관객 수 기준으로 가장 큰 비중을 차지한다.",
    label_visibility="collapsed",
    key="insight_genre_treemap",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 3. 총 관객 히스토그램
# -----------------------------------------------------------------------
st.header("3. 총 관객 수 히스토그램")

N_BINS = 20

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=N_BINS,
)
fig_hist.update_traces(
    hovertemplate="관객 구간: %{x}<br>영화 편수: %{y}편<extra></extra>",
)
fig_hist.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    bargap=0.05,
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_hist, use_container_width=True)

# 가장 영화가 많이 몰려 있는 구간 계산
counts, bin_edges = np.histogram(df["total_audi"].dropna(), bins=N_BINS)
max_bin_idx = counts.argmax()
bin_start, bin_end = bin_edges[max_bin_idx], bin_edges[max_bin_idx + 1]

# 총 관객이 가장 많은 영화 계산
top_row = df.loc[df["total_audi"].idxmax()]

st.markdown(
    f"- 가장 많은 영화가 몰려 있는 구간은 **약 {bin_start:,.0f}명 ~ {bin_end:,.0f}명** "
    f"사이로, 이 구간에 **{counts[max_bin_idx]}편**의 영화가 속해 있습니다.\n"
    f"- 총 관객이 가장 많은 영화는 **『{top_row['movieNm']}』**이며, "
    f"총 관객 수는 **{top_row['total_audi']:,.0f}명**입니다."
)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="총 관객 히스토그램 해석",
    value="",
    placeholder="예: 대부분의 영화는 총 관객 ○○명 이하에 몰려 있고, 일부 영화만 압도적으로 많은 관객을 동원했다.",
    label_visibility="collapsed",
    key="insight_audi_hist",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 4. 개봉일 스크린수 vs 총 관객 산점도 (장르별 색상)
# -----------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
)
fig_scatter.update_traces(
    hovertemplate="영화명: %{hovertext}<br>개봉일 스크린수: %{x:,}개<br>총 관객: %{y:,}명<extra></extra>",
)
fig_scatter.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="스크린수-총 관객 산점도 해석",
    value="",
    placeholder="예: 개봉일 스크린수가 많을수록 대체로 총 관객도 많아지는 경향이 있으며, ○○ 장르가 특히 그렇다.",
    label_visibility="collapsed",
    key="insight_scrn_audi_scatter",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 5. 영화 10편 이상인 장르의 총 관객 박스플롯
# -----------------------------------------------------------------------
st.header("5. 장르별 총 관객 분포 (영화 10편 이상인 장르)")

genre_movie_counts = df["genre"].value_counts()
major_genres = genre_movie_counts[genre_movie_counts >= 10].index
df_major_genres = df[df["genre"].isin(major_genres)]

fig_box = px.box(
    df_major_genres,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    hover_data={"movieNm": True, "genre": False},
)
fig_box.update_traces(
    hovertemplate="영화명: %{customdata[0]}<br>총 관객: %{y:,}명<extra></extra>",
)
fig_box.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    showlegend=False,
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="장르별 총 관객 박스플롯 해석",
    value="",
    placeholder="예: ○○ 장르는 총 관객의 중앙값이 가장 높고, 일부 영화가 상자 밖으로 튀어나올 만큼 관객을 크게 동원했다.",
    label_visibility="collapsed",
    key="insight_genre_audi_box",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 6. 개봉일 스크린수 vs 총 관객 버블 그래프 (점 크기 = 첫 주 관객)
# -----------------------------------------------------------------------
st.header("6. 개봉일 스크린수와 총 관객의 관계 (버블 크기 = 첫 주 관객)")

fig_bubble = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    size_max=40,
)
fig_bubble.update_traces(
    hovertemplate=(
        "영화명: %{hovertext}<br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "첫 주 관객: %{marker.size:,}명<extra></extra>"
    ),
)
fig_bubble.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title_text="장르",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="스크린수-총 관객 버블 그래프 해석",
    value="",
    placeholder="예: 버블이 클수록(첫 주 관객이 많을수록) 총 관객도 함께 많아지는 경향이 있다.",
    label_visibility="collapsed",
    key="insight_scrn_audi_bubble",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 7. 제작 국가 -> 장르 선버스트 (칸 크기 = 영화 편수)
# -----------------------------------------------------------------------
st.header("7. 제작 국가별 장르 구성 선버스트")

nation_genre_counts = (
    df.groupby(["nation", "genre"]).size().reset_index(name="count")
)

fig_sunburst = px.sunburst(
    nation_genre_counts,
    path=["nation", "genre"],
    values="count",
)
fig_sunburst.update_traces(
    hovertemplate="%{label}<br>영화 편수: %{value}편<extra></extra>",
)
fig_sunburst.update_layout(
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="국가별 장르 선버스트 해석",
    value="",
    placeholder="예: ○○ 국가에서 제작된 영화 중에서는 ○○ 장르의 비중이 가장 크다.",
    label_visibility="collapsed",
    key="insight_nation_genre_sunburst",
)

st.divider()


# -----------------------------------------------------------------------
# 그래프 8. 개봉 월별 영화 편수 (막대 색 = 월평균 총 관객) - 성수기 효과
# -----------------------------------------------------------------------
st.header("8. 개봉 월별 영화 편수와 평균 총 관객 - 성수기 효과")

df_month = df.dropna(subset=["openDt"]).copy()
df_month["open_month"] = df_month["openDt"].dt.month

monthly_stats = (
    df_month.groupby("open_month")
    .agg(count=("movieNm", "size"), avg_total_audi=("total_audi", "mean"))
    .reindex(range(1, 13), fill_value=0)
    .reset_index()
)
monthly_stats["open_month"] = monthly_stats["open_month"].astype(str) + "월"

fig_month = px.bar(
    monthly_stats,
    x="open_month",
    y="count",
    color="avg_total_audi",
    color_continuous_scale="Reds",
)
fig_month.update_traces(
    hovertemplate="%{x}<br>개봉 편수: %{y}편<br>월평균 총 관객: %{marker.color:,.0f}명<extra></extra>",
)
fig_month.update_layout(
    xaxis_title="개봉 월",
    yaxis_title="개봉 편수",
    coloraxis_colorbar_title="월평균<br>총 관객",
    margin=dict(t=30, b=30, l=10, r=10),
)

st.plotly_chart(fig_month, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.text_area(
    label="개봉 월별 편수/관객 해석",
    value="",
    placeholder="예: ○월에 개봉 편수와 평균 총 관객이 모두 높아, 이른바 성수기 효과가 나타난다.",
    label_visibility="collapsed",
    key="insight_month_release_bar",
)

st.divider()

st.caption(
    "※ 이후 분포와 관계를 보여 주는 그래프를 "
    "이 아래에 같은 형식(그래프 + '이 그래프로 알 수 있는 것')으로 계속 추가할 수 있습니다."
)
