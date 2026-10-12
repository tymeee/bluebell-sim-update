# pages/1_Fund_Information.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Fund Information",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown(
    """
    <style>
    /* =========================================
       BLUEBELL FUND INFORMATION PAGE
       ========================================= */

    :root {
        --bb-background: #06101f;
        --bb-background-secondary: #08182d;
        --bb-card: rgba(13, 34, 61, 0.88);
        --bb-card-hover: rgba(17, 43, 76, 0.94);
        --bb-border: rgba(105, 162, 230, 0.20);
        --bb-border-hover: rgba(105, 162, 230, 0.42);
        --bb-primary: #6fa7ff;
        --bb-primary-soft: rgba(89, 145, 230, 0.15);
        --bb-text: #f3f7ff;
        --bb-text-secondary: #aebed5;
        --bb-text-muted: #8194af;
    }


    /* =========================================
       OVERALL PAGE
       ========================================= */

    html,
    body,
    .stApp,
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(
                circle at 15% 0%,
                rgba(32, 91, 159, 0.20),
                transparent 31rem
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(28, 80, 146, 0.13),
                transparent 28rem
            ),
            linear-gradient(
                160deg,
                var(--bb-background-secondary),
                var(--bb-background) 55%,
                #040b16
            ) !important;

        color: var(--bb-text);
    }

    [data-testid="stAppViewContainer"] {
        min-height: 100vh;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* =========================================
       STREAMLIT HEADER
       ========================================= */

    /* Header appears at the top initially but does not stay fixed while scrolling */
    /* Header scrolls away with the page */
    [data-testid="stHeader"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
    
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        overflow: visible !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    
    /* Desktop sidebar control */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        z-index: 999999 !important;
    }
    
    
    /* Keep only the sidebar-opening button visible on mobile */
    @media (max-width: 768px) {
    
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stExpandSidebarButton"] {
            position: fixed !important;
    
            top: 0.7rem !important;
            left: 0.7rem !important;
            right: auto !important;
    
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
    
            align-items: center !important;
            justify-content: center !important;
    
            width: 44px !important;
            height: 44px !important;
    
            border: 1px solid rgba(179, 203, 228, 0.35) !important;
            border-radius: 12px !important;
    
            background: rgba(16, 35, 54, 0.94) !important;
            color: #ffffff !important;
    
            box-shadow: 0 8px 24px rgba(2, 10, 18, 0.30) !important;
    
            z-index: 9999999 !important;
        }
    
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stExpandSidebarButton"] svg {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
    
        /* Prevent page content from sitting underneath the button */
        .block-container {
            padding-top: 3.7rem !important;
        }
    }


    /* =========================================
       PAGE TITLES
       ========================================= */

    h1 {
        color: var(--bb-text) !important;
        font-size: clamp(2.1rem, 4vw, 3.7rem) !important;
        line-height: 1.05 !important;
        font-weight: 780 !important;
        letter-spacing: -0.045em !important;
        margin-bottom: 0.7rem !important;
    }

    h1::after {
        content: "";
        display: block;
        width: 72px;
        height: 4px;
        margin-top: 0.75rem;

        border-radius: 999px;

        background: linear-gradient(
            90deg,
            #75aaff,
            rgba(117, 170, 255, 0.08)
        );
    }

    h2,
    h3 {
        color: var(--bb-text) !important;
        letter-spacing: -0.025em;
    }

    [data-testid="stMarkdownContainer"] p {
        color: var(--bb-text-secondary);
        line-height: 1.7;
    }


    /* =========================================
       DISCLAIMER / DATA NOTE
       ========================================= */

    .fund-data-note {
        display: flex;
        align-items: center;
        gap: 0.65rem;

        width: fit-content;
        max-width: 100%;

        margin: 0.5rem 0 1.8rem;
        padding: 0.75rem 1rem;

        border: 1px solid rgba(108, 159, 226, 0.18);
        border-radius: 13px;

        background: rgba(14, 37, 66, 0.64);

        color: var(--bb-text-secondary);
        font-size: 0.88rem;
        line-height: 1.5;

        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.18);
    }

    .fund-data-note::before {
        content: "i";
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;

        width: 21px;
        height: 21px;

        border: 1px solid rgba(117, 170, 255, 0.45);
        border-radius: 50%;

        color: #a9caff;
        font-size: 0.75rem;
        font-weight: 750;
    }


    /* =========================================
       SIDEBAR
       ========================================= */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(10, 28, 51, 0.98),
                rgba(5, 16, 31, 0.99)
            ) !important;

        border-right: 1px solid rgba(105, 162, 230, 0.16);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.6rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--bb-text) !important;
    }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #c5d3e7 !important;
        font-size: 0.92rem !important;
        font-weight: 650 !important;
        letter-spacing: 0.01em;
    }


    /* Fund-selection radio cards */

    [data-testid="stSidebar"] [data-baseweb="radio"] {
        width: 100%;
        margin-bottom: 0.34rem;
        padding: 0.66rem 0.75rem;

        border: 1px solid transparent;
        border-radius: 12px;

        background: rgba(12, 32, 58, 0.54);

        transition:
            background 160ms ease,
            border-color 160ms ease,
            transform 160ms ease;
    }

    [data-testid="stSidebar"] [data-baseweb="radio"]:hover {
        transform: translateX(3px);
        border-color: rgba(107, 161, 229, 0.25);
        background: rgba(18, 45, 78, 0.78);
    }

    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
        border-color: rgba(112, 168, 241, 0.48);
        background:
            linear-gradient(
                135deg,
                rgba(39, 89, 154, 0.44),
                rgba(20, 50, 88, 0.78)
            );

        box-shadow:
            inset 3px 0 0 #71a8ff,
            0 8px 25px rgba(0, 0, 0, 0.16);
    }

    [data-testid="stSidebar"] [data-baseweb="radio"] p {
        color: #dce7f7 !important;
        font-size: 0.91rem;
        line-height: 1.3;
    }


    /* =========================================
       METRIC CARDS
       ========================================= */

    [data-testid="stMetric"] {
        /* Normal consistent card size */
        min-height: 135px;
        height: auto;
    
        padding: 1.35rem 1.4rem;
    
        background:
            linear-gradient(
                145deg,
                rgba(17, 38, 66, 0.90),
                rgba(8, 21, 40, 0.88)
            );
    
        border: 1px solid var(--border);
        border-radius: 20px;
    
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
    
        box-sizing: border-box;
        overflow: visible;
    
        transition:
            transform 180ms ease,
            border-color 180ms ease,
            box-shadow 180ms ease;
    }
    
    /* Allow long labels to wrap and increase the card height */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p {
        color: var(--text-secondary) !important;
        font-weight: 550;
    
        white-space: normal !important;
        overflow-wrap: anywhere;
        word-break: normal;
    
        line-height: 1.35;
    }
    
    /* Allow unusually long values to wrap rather than escape the card */
    [data-testid="stMetricValue"] {
        color: var(--text-main) !important;
    
        font-size: 2rem;
        font-weight: 720;
        letter-spacing: -0.035em;
        line-height: 1.12;
    
        white-space: normal !important;
        overflow-wrap: anywhere;
    }

    @media (max-width: 900px) {
    [data-testid="stMetric"] {
        min-height: 110px;
        height: auto;
    }
    }
    /* =========================================
       PLOTLY CHART CARDS
       ========================================= */

    [data-testid="stPlotlyChart"] {
        margin: 1rem 0 1.6rem;
        padding: 0.7rem;

        overflow: hidden;

        border: 1px solid var(--bb-border);
        border-radius: 22px;

        background:
            linear-gradient(
                145deg,
                rgba(12, 31, 56, 0.92),
                rgba(6, 19, 37, 0.90)
            );

        box-shadow:
            0 24px 65px rgba(0, 0, 0, 0.26),
            inset 0 1px 0 rgba(255, 255, 255, 0.025);
    }

    [data-testid="stPlotlyChart"] .js-plotly-plot,
    [data-testid="stPlotlyChart"] .plot-container,
    [data-testid="stPlotlyChart"] .svg-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Make default Plotly line charts fit the dark page */

    [data-testid="stPlotlyChart"] .main-svg {
        background: transparent !important;
    }

    [data-testid="stPlotlyChart"] .main-svg .bg {
        fill: rgba(5, 17, 33, 0.42) !important;
    }

    [data-testid="stPlotlyChart"] .gridlayer path {
        stroke: rgba(136, 171, 214, 0.13) !important;
    }

    [data-testid="stPlotlyChart"] .zerolinelayer path {
        stroke: rgba(136, 171, 214, 0.22) !important;
    }

    [data-testid="stPlotlyChart"] .xtick text,
    [data-testid="stPlotlyChart"] .ytick text,
    [data-testid="stPlotlyChart"] .xtitle,
    [data-testid="stPlotlyChart"] .ytitle,
    [data-testid="stPlotlyChart"] .gtitle {
        fill: #c8d6e9 !important;
    }

    /* Remove the visible top toolbar while preserving mobile sidebar access */
    [data-testid="stHeader"] {
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }
    
    
    /* Hide Streamlit's thin decorative header line */
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    /* Hide status/busy widget from the header area */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }
    .block-container {
    padding-top: 0.8rem !important;
    }

    @media (max-width: 768px) {
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;

        position: fixed !important;
        top: 0.65rem !important;
        left: 0.65rem !important;
        z-index: 999999 !important;
    }

    .block-container {
        padding-top: 3.7rem !important;
    }
    }
    /* =========================================
       MOBILE
       ========================================= */

    @media (max-width: 768px) {

        .block-container {
            width: 100%;
            padding-top: 1.2rem;
            padding-left: 0.75rem;
            padding-right: 0.75rem;
            padding-bottom: 3rem;
        }

        h1 {
            font-size: 2.15rem !important;
            line-height: 1.08 !important;
            letter-spacing: -0.035em !important;
        }

        h1::after {
            width: 54px;
            height: 3px;
        }

        .fund-data-note {
            width: 100%;
            margin-bottom: 1.25rem;
            padding: 0.7rem 0.8rem;
            font-size: 0.8rem;
        }

        /*
           Stack all metric columns vertically.
           This also prevents narrow metric cards.
        */
        [data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.7rem !important;
        }

        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        [data-testid="stMetric"] {
            min-height: 105px;
            padding: 1rem 1.05rem;
            border-radius: 16px;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }

        [data-testid="stMetricLabel"] p {
            font-size: 0.82rem !important;
        }

        [data-testid="stPlotlyChart"] {
            margin: 0.8rem 0 1.1rem;
            padding: 0.15rem;
            border-radius: 17px;
        }

        [data-testid="stSidebar"] {
            width: min(88vw, 350px) !important;
        }

        [data-testid="stSidebar"] [data-baseweb="radio"] {
            padding: 0.72rem 0.7rem;
        }

        [data-testid="stSidebarCollapsedControl"],
        [data-testid="stExpandSidebarButton"] {
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;

            border: 1px solid rgba(112, 168, 241, 0.30) !important;
            border-radius: 12px !important;

            background: rgba(8, 25, 47, 0.94) !important;
        }
    }


    @media (max-width: 420px) {

        .block-container {
            padding-left: 0.55rem;
            padding-right: 0.55rem;
        }

        h1 {
            font-size: 1.9rem !important;
        }

        [data-testid="stMetric"] {
            min-height: 98px;
        }

        [data-testid="stPlotlyChart"] {
            border-radius: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Fund Information")
st.write("Disclaimer: Data was last updated on July 17 2026, future changes may not have been accounted for")

def get_data():
    master_doc = pd.read_csv("mutualfunds_data.csv")
    return master_doc
historicaldata = get_data()

available_fund =[ 
    "KKP Plus",
    "KKP Cash",
    "KFAFIX",
    "UGISFX",
    "ESGQG",
    "ESGTECH",
    "ESEAE",
    "KTPRECIOUS",
    "KKPGNPH",
    "KTHEALTHCAREA",
    "KFGPROPA",
    "SCBS&P500A",
    "ESGCORE"
]
fund = st.sidebar.radio( 
    "Fund Selection",
    available_fund)

if fund == "KKP Plus":
    st.title("KKP Plus")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="1.49%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="3.71"
    )

    c3.metric(
        label="Risk Level",
        value="Low"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["plus"] = pd.to_numeric(
        historicaldata["plus"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "plus"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="plus",
        title="Historical Price",
        labels={
        "plus": "KKP Plus price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Japan Treasury Disc Bill(JP1743701S35)",
        "พันธบัตรธนาคารแห่งประเทศไทย (CBF26O12A)",
        "พันธบัตรธนาคารแห่งประเทศไทย (CBF26817A)",
        "JAPAN TREASURY DISC BILL (JP1743801S59)",
        "พันธบัตรธนาคารแห่งประเทศไทย (CBF26720A)",
        "Other"
    ]
    alloc_amt = [
        0.058,
        0.055,
        0.0454,
        0.0417,
        0.0317,
        0.7628
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )


    st.plotly_chart(pie_fig, width = "stretch",config={"responsive":True,"displayModeBar":False})
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Bonds/Treasury Bills")
    
if fund == "KKP Cash":
    st.title("KKP Cash")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="1.29%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="2.01"
    )

    c3.metric(
        label="Risk Level",
        value="Low"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["cash"] = pd.to_numeric(
        historicaldata["cash"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "cash"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="cash",
        title="Historical Price",
        labels={
        "cash": "KKP Cash price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "พันธบัตรธนาคารแห่งประเทศไทย (CBF26907A)",
        "JAPAN TREASURY DISC BILL (JP1743701S35)",
        "พันธบัตรธนาคารแห่งประเทศไทย (CBF26824A)",
        "พันธบัตรธนาคารแห่งประเทศไทย (CBF26817A)",
        "JAPAN TREASURY DISC BILL (JP1743781S53)",
        "Other"
    ]
    alloc_amt = [
        0.0977,
        0.0757,
        0.054,
        0.05,
        0.0474,
        0.6752
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Money Market Assets")

if fund == "KFAFIX":
    st.title("KFAFIX-A")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="3.41%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="-0.22"
    )

    c3.metric(
        label="Risk Level",
        value="Low"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["kfa"] = pd.to_numeric(
        historicaldata["kfa"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "kfa"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="kfa",
        title="Historical Price",
        labels={
        "kfa": "KFAFIX-A price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Doha Bank Deposit Account",
        "Gulf Development Bond (ครั้งที่ 1/2568 ชุดที่ 2)",
        "พันธบัตรธนาคารแห่งประเทศไทยงวดที่ 3/364/69",
        "PIMCO GIS Income Fund",
        "พันธบัตรรัฐบาลส่งเสริมความยั่งยืน ใน ปีงบประมาณ พ.ศ. 2568 ครั้งที่1",
        "Other"
    ]
    alloc_amt = [
        0.0833,
        0.0577,
        0.0471,
        0.0452,
        0.0389,
        0.7278
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Corporate Debt Instruments")

if fund == "UGISFX":
    st.title("UGISFX-N")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="1.26%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="1.47"
    )

    c3.metric(
        label="Risk Level",
        value="Low"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["ugi"] = pd.to_numeric(
        historicaldata["ugi"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "ugi"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="ugi",
        title="Historical Price",
        labels={
        "ugi": "UGISFX-N price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "PIMCO GIS Income Fund (Class I)",
        "Other"
    ]
    alloc_amt = [
        0.9654,
        0.0346
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Bonds")

if fund == "ESGQG":
    st.title("ES-GQG")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="12.33%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="0.79"
    )

    c3.metric(
        label="Risk Level",
        value="High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["gqg"] = pd.to_numeric(
        historicaldata["gqg"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "gqg"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="gqg",
        title="Historical Price",
        labels={
        "gqg": "ES-GQG price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Wellington Global Quality Growth Fund",
        "Other"
    ]
    alloc_amt = [
        0.9773,
        0.0227
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Equity")


if fund == "ESGTECH":
    st.title("ES-GTECH")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="44.53%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="2.06"
    )

    c3.metric(
        label="Risk Level",
        value="Very High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["gtech"] = pd.to_numeric(
        historicaldata["gtech"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "gtech"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="gtech",
        title="Historical Price",
        labels={
        "gtech": "ES-GTECH price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Polar Capital Global Technology Fund USD Class I Dist (POLGTIU)",
        "Other"
    ]
    alloc_amt = [
        0.9796,
        0.0204
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Technology Sector Equity")

if fund == "ESEAE":
    st.title("ES-EAE")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="27.46%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="1.57"
    )

    c3.metric(
        label="Risk Level",
        value="High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["eae"] = pd.to_numeric(
        historicaldata["eae"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "eae"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="eae",
        title="Historical Price",
        labels={
        "eae": "ES-EAE price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Baillie Gifford Worldwide Emerging Markets Leading Companies Fund",
        "Other"
    ]
    alloc_amt = [
        0.9588,
        0.0412
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Emerging Market Equity")    

if fund == "KTPRECIOUS":
    st.title("KT-PRECIOUS")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="163.05%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="1.23"
    )

    c3.metric(
        label="Risk Level",
        value="Very High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["ktp"] = pd.to_numeric(
        historicaldata["ktp"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "ktp"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="ktp",
        title="Historical Price",
        labels={
        "ktp": "KT-PRECIOUS price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Franklin Templeton Investment Funds - Franklin Gold and Precious Metals Fund A SGD",
        "Other"
    ]
    alloc_amt = [
        0.9742,
        0.0258
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Commodities (Gold/Precious Metals)")

if fund == "KKPGNPH":
    st.title("KKP GNP-H")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="14.43%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="0.7"
    )

    c3.metric(
        label="Risk Level",
        value="High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["gnph"] = pd.to_numeric(
        historicaldata["gnph"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "gnph"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="gnph",
        title="Historical Price",
        labels={
        "gnph": "KKP GNP-H price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "CAPITAL GROUP NEW PERSPECTIVE FUND LUX",
        "BAY",
        "STANDARD CHARTERED BANK (THAI) PUBLIC CO.,LTD.",
        "KIATNAKIN PHATRA ASSET MANAGEMENT COMPANY LIMITED",
        "Other"
    ]
    alloc_amt = [
        0.9657,
        0.0171,
        0.0108,
        0.0024,
        0.004
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Equity")

if fund == "KTHEALTHCAREA":
    st.title("KT-HEALTHCARE-A")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="16.05%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="1.87"
    )

    c3.metric(
        label="Risk Level",
        value="Very High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["healthcare"] = pd.to_numeric(
        historicaldata["healthcare"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "healthcare"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="healthcare",
        title="Historical Price",
        labels={
        "healthcare": "KT-HEALTHCARE-A price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Janus Global Life Sciences Fund",
        "Other"
    ]
    alloc_amt = [
        0.9851,
        0.0149
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Healthcare Sector Equity")


if fund == "KFGPROPA":
    st.title("KFGPROP-A")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="3.58%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="0.6"
    )

    c3.metric(
        label="Risk Level",
        value="Very High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["prop"] = pd.to_numeric(
        historicaldata["prop"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "prop"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="prop",
        title="Historical Price",
        labels={
        "prop": "KFGPROP-A price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Janus Capital International Ltd",
        "Other"
    ]
    alloc_amt = [
        0.9578,
        0.0422
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Property/Real Estate Sector Equity")

if fund == "ESGCORE":
    st.title("ES-GCORE")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="18.04%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="1.23"
    )

    c3.metric(
        label="Risk Level",
        value="High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["gcore"] = pd.to_numeric(
        historicaldata["gcore"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "gcore"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="gcore",
        title="Historical Price",
        labels={
        "gcore": "ES-GCORE price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "Goldman Sachs - SICAV I - GS Global CORE Eq Ptf",
        "Other"
    ]
    alloc_amt = [
        0.9742,
        0.0258
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="Global Equity")

if fund == "SCBS&P500A":
    st.title("SCBS&P500A")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        label="1 year return (2025)",
        value="12.07%"
    )

    c2.metric(
        label="1 year Sharpe Ratio (2025)",
        value="1.2"
    )

    c3.metric(
        label="Risk Level",
        value="High"
    )

    st.write("Historical Price Data (Since End of 2024)")

    historicaldata["Date"] = pd.to_datetime(
        historicaldata["Date"],
        errors="coerce"
    )

    historicaldata["sp500"] = pd.to_numeric(
        historicaldata["sp500"],
        errors="coerce"
    )

    plot_data = (
        historicaldata
        .dropna(subset=["Date", "sp500"])
        .sort_values("Date")
    )

    fig = px.line(
        plot_data,
        x="Date",
        y="sp500",
        title="Historical Price",
        labels={
        "sp500": "SCBS&P500A price",
        "Date": "Date"
        }
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Fund Price",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch",
        config={"displayModeBar": False}
    )

    Holdings = [
        "ISHARES CORE S&P 500 ETF",
        "JP MORGAN US RESEARCH ENHANCED INDEX EQUITY ACTIVE UCITS ETF",
        "Other"
    ]
    alloc_amt = [
        0.9881,
        0.0098,
        0.0021
    ]
    pie_fig = px.pie(Holdings,values=alloc_amt,names = Holdings, title = "Top 5 Fund Holdings")
    pie_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=13,
            color="#F5F8FF"
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{percent}"
            "<extra></extra>"
        ),
        marker=dict(
            line=dict(
                color="#071121",
                width=2
            )
        )
      )
    pie_fig.update_layout(
        title=dict(
            text="Top 5 Fund Holdings",
            x=0.02,
            xanchor="left",
            font=dict(
                size=20,
                color="#F1F6FF"
            )
        ),

        height=520,

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            family="Inter, Arial, sans-serif",
            color="#D9E5F5"
        ),

    # Put legend below chart so it cannot get cut off
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.08,
            yanchor="top",
            font=dict(
                size=12,
                color="#D9E5F5"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),

        margin=dict(
            l=25,
            r=25,
            t=75,
            b=100
        )
      )
    st.plotly_chart(pie_fig, use_container_width = True)
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Main Asset Class", value="S&P500 and American Equity")
