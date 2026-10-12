"""Original BlueBridge presentation with the optimized computation service.

Upstream UI: tymeee/monte-carlo-retirement-simulation, commit ffe9409.
Engine: fast_simulator. Monthly plot samples and corrected per-trial statistics.
"""
import os
import time
import base64
from pathlib import Path
from copy import deepcopy
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import httpx
import streamlit as st
from fast_simulator.schema import SimulationRequest, INDEX_NAMES, FUND_NAMES

st.set_page_config(
    page_title="Monte Carlo Retirement Simulator",
    layout="wide",
    initial_sidebar_state="auto"
)

logo_path = Path("bluebridgeai1-removebg-preview.png")

if logo_path.exists():
    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")
else:
    logo_base64 = ""

st.html(Path("style.css"))
st.html(
    f"""
    <section class="mc-hero">
        <div class="mc-hero-content">
            <div class="mc-eyebrow">
                BLUEBRIDGE PORTFOLIO SIMULATOR
            </div>

            <h1 class="mc-hero-title">
                Plan your retirement with
                <span>BLUEBRIDGE</span>
            </h1>

            <p class="mc-hero-description">
                Explore potential portfolio outcomes, compare investment
                strategies, and understand how contributions, withdrawals,
                and market uncertainty may affect your financial plan.
            </p>
        </div>

        <div class="mc-logo-area">
            <div class="mc-logo-glow"></div>

            <img
                class="mc-bluebell-logo"
                src="data:image/png;base64,{logo_base64}"
                alt="Bluebell logo"
            >
        </div>
    </section>
    """
)

from button import thb_number_input, load_thb_input_styles
load_thb_input_styles()

def style_line_chart(fig, title):
    fig.update_layout(title=dict(text=title, x=0.02, xanchor='left', y=0.97, yanchor='top', font=dict(size=21, color='#F1F6FF')), autosize=True, height=620, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(5,13,27,0.35)', font=dict(family='Inter, Arial, sans-serif', size=13, color='#B8C8DD'), legend=dict(orientation='h', x=0.5, xanchor='center', y=1.02, yanchor='bottom', bgcolor='rgba(0,0,0,0)', font=dict(size=12, color='#D9E5F5'), itemwidth=55), margin=dict(l=70, r=35, t=125, b=65), hovermode='x unified', hoverlabel=dict(bgcolor='#0D1B31', bordercolor='#315989', font=dict(color='#F1F6FF')))
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True, linecolor='rgba(140,180,235,0.15)', tickfont=dict(color='#A8BAD4'), title_font=dict(color='#DCE8F8'))
    fig.update_yaxes(showgrid=True, gridcolor='rgba(140,180,235,0.13)', zeroline=False, automargin=True, linecolor='rgba(140,180,235,0.15)', tickfont=dict(color='#A8BAD4'), title_font=dict(color='#DCE8F8'))
    return fig

def index_controls():
    time_period = acum_years + retirement_years
    st.sidebar.subheader("Portfolio")
    available_fund = [
      "US Equity",
      "Thai Equity",
      "China Equity",
      "Bond/Fixed Income Fund",
      "Aggressive Mutual Fund",
      "Moderate Mutual Fund",
      "Conservative Mutual Fund",
      "Savings",
      "Technology Sector Fund",
      "Healthcare Sector Fund",
      "Property/Real Estate Fund",
      "Commodity Fund",
      "Global Equity Fund",
      "Emerging Market Fund"
    ]
    selection = st.sidebar.multiselect(
        "Select Funds",
        available_fund)
    if "US Equity" in selection:
        us_weight = st.sidebar.slider(
            "US Equity",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        us_weight = 0
    if "Thai Equity" in selection:
        thai_weight = st.sidebar.slider(
            "Thai Equity",
            0.0,
            1.0,
            0.0,
            0.01
            )
    else:
        thai_weight = 0
    if "China Equity" in selection:
        china_weight = st.sidebar.slider(
            "Chinese Equity",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        china_weight = 0
    if "Bond/Fixed Income Fund" in selection:
        bond_weight = st.sidebar.slider(
            "Bond Fund",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        bond_weight = 0
    if "Aggressive Mutual Fund" in selection:
        agg_weight = st.sidebar.slider(
            "Aggressive Hybrid Fund",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        agg_weight = 0
    if "Moderate Mutual Fund" in selection:
        mod_weight = st.sidebar.slider(
            "Moderate Hybrid Fund",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        mod_weight = 0
    if "Conservative Mutual Fund" in selection:
        cons_weight = st.sidebar.slider(
            "Conservative Hybrid Fund",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        cons_weight = 0
    if "Savings" in selection:
        savings_weight = st.sidebar.slider(
            "Savings",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else: 
        savings_weight = 0
    if "Technology Sector Fund" in selection:
        technology_weight = st.sidebar.slider(
            "Technology Sector index",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        technology_weight = 0
    if "Global Equity Fund" in selection:
        globalequity_weight = st.sidebar.slider(
            "Global Equity index",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        globalequity_weight = 0
    if "Healthcare Sector Fund" in selection:
        healthcare_weight = st.sidebar.slider(
            "Healthcare index",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        healthcare_weight = 0
    if "Property/Real Estate Fund" in selection:
        property_weight = st.sidebar.slider(
            "Property and Real Estate Index",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        property_weight = 0
    if "Emerging Market Fund" in selection:
        emerging_weight = st.sidebar.slider(
            "Emerging Markets Index",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else:
        emerging_weight = 0
    if "Commodity Fund" in selection:
        commodity_weight = st.sidebar.slider(
            "Commodity Index",
            0.0,
            1.0,
            0.0,
            0.01
        )
    else: 
        commodity_weight = 0
    total_weight = (
        us_weight +
        thai_weight +
        china_weight +
        bond_weight +
        agg_weight +
        mod_weight +
        cons_weight +
        savings_weight + 
        globalequity_weight + 
        healthcare_weight +
        technology_weight + 
        property_weight + 
        emerging_weight +
        commodity_weight
    )

    st.sidebar.write(
        f"Total Weight: {total_weight:.2f}"
    )

    if total_weight > 1:
        st.error(
            "Weights exceed 100%"
        )
        st.sidebar.error(
          f"Allocated: {total_weight:.0%}. "
          "Reduce the allocation to 100% or less."
          )    
        st.stop()
    import pandas as pd
    import plotly.express as px
    pure_cash = 1 - total_weight
    allocation_data = pd.DataFrame({
      "Asset": [
          "US Equity",
          "Thai Equity",
          "China Equity",
          "Bond Mutual Fund",
          "Aggresive Hybrid Mutual Fund",
          "Moderate Hybrid Mutual Fund",
          "Conservative Hybrid Mutual Fund",
          "Global Equity Index",
          "Healthcare Index",
          "Technology Index",
          "Property and Real Estate Index",
          "Emerging Markets Index",
          "Commodity Index",
          "Savings Account",
          "Pure Cash"
      ],
      "Allocation": [
          us_weight,
          thai_weight,
          china_weight,
          bond_weight,
          agg_weight,
          mod_weight,
          cons_weight,
          globalequity_weight,
          healthcare_weight,
          technology_weight,
          property_weight,
          emerging_weight,
          commodity_weight,
          savings_weight,
          pure_cash
          ]
      })

    allocation_data = allocation_data[
          allocation_data["Allocation"] > 0
    ]
    return {name: float(value) for name,value in zip(INDEX_NAMES + ['Savings'], [us_weight, thai_weight, china_weight, bond_weight, agg_weight, mod_weight, cons_weight, globalequity_weight, healthcare_weight, technology_weight, property_weight, emerging_weight, commodity_weight, savings_weight])}, 'Custom'


def fund_controls():
    available_funds = [
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
    preset = st.sidebar.radio(
      "Portfolio",
      ["Custom", "Bluebell Basic", "Bluebell Balance", "Bluebell Beyond"]
    )
    if preset == "Bluebell Basic":
        gnph_alloc = 0.0
        healthcarea_alloc = 0.05
        gtech_alloc = 0.05
        propa_alloc = 0.05
        kkpplus_alloc = 0.35
        kfa_alloc = 0.3
        ugi_alloc = 0.1
        kkpcash_alloc = 0
        gqg_alloc = 0
        eae_alloc = 0
        ktprecious_alloc = 0
        rostrum_alloc = 0
        sp500a_alloc = 0 
        gcore_alloc = 0.1
    elif preset == "Bluebell Balance":
        gnph_alloc = 0.0
        healthcarea_alloc = 0.05
        gtech_alloc = 0.05
        propa_alloc = 0.05
        kkpplus_alloc = 0.15
        kfa_alloc = 0.2
        ugi_alloc = 0.1
        kkpcash_alloc = 0
        gqg_alloc = 0
        eae_alloc = 0.05
        ktprecious_alloc = 0
        rostrum_alloc = 0
        sp500a_alloc = 0.1
        gcore_alloc = 0.25
    elif preset == "Bluebell Beyond":
        gnph_alloc = 0.0
        healthcarea_alloc = 0.1
        gtech_alloc = 0.1
        propa_alloc = 0.1
        kkpplus_alloc = 0.05
        kfa_alloc = 0.05
        ugi_alloc = 0.05
        kkpcash_alloc = 0
        gqg_alloc = 0
        eae_alloc = 0.1
        ktprecious_alloc = 0
        rostrum_alloc = 0
        sp500a_alloc = 0.1
        gcore_alloc = 0.35
    elif preset == "Custom":
        selected_funds = st.sidebar.multiselect(
          "Select Funds",
          available_funds,
          default=["KKP Plus","KKP Cash"]
        )
        if "KKP Plus" in selected_funds:
            kkpplus_alloc = st.sidebar.slider(
              "KKP Plus",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else: 
            kkpplus_alloc = 0

        if "KKP Cash" in selected_funds:
            kkpcash_alloc = st.sidebar.slider(
                "KKP Cash",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            kkpcash_alloc = 0

        if "KFAFIX" in selected_funds:
            kfa_alloc = st.sidebar.slider(
                "KFAFIX",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            kfa_alloc = 0

        if "UGISFX" in selected_funds:
            ugi_alloc = st.sidebar.slider(
                "UGISFX",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            ugi_alloc = 0

        if "ESGQG" in selected_funds:
            gqg_alloc = st.sidebar.slider(
                "ESGQG",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            gqg_alloc = 0

        if "ESGTECH" in selected_funds:
          gtech_alloc = st.sidebar.slider(
            "ESGTECH",
            0.0,
            1.0,
            0.0,
            0.01
          )
        else:
            gtech_alloc = 0

        if "ESEAE" in selected_funds:
            eae_alloc = st.sidebar.slider(
                "ESEAE",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            eae_alloc = 0

        if "KTPRECIOUS" in selected_funds:
            ktprecious_alloc = st.sidebar.slider(
                "KTPRECIOUS",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            ktprecious_alloc = 0 
        if "Rostrum Wisdom Fund of Funds" in selected_funds:
            rostrum_alloc = st.sidebar.slider(
                "Rostrum Grand Wisdom Fund of Funds",
                0.0,
                1.0,
                0.0,
                0.01
            ) 
        else:
            rostrum_alloc = 0
        if "KKPGNPH" in selected_funds:
            gnph_alloc = st.sidebar.slider(
                "KKPGNPH",
                0.0,
                1.0,
                0.0,
                0.01
            ) 
        else:
            gnph_alloc = 0 
        if "KTHEALTHCAREA" in selected_funds:
            healthcarea_alloc = st.sidebar.slider(
                "KTHEALTHCAREA",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            healthcarea_alloc = 0
        if "KFGPROPA" in selected_funds:
            propa_alloc = st.sidebar.slider(
                "KFGPROPA",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else: 
            propa_alloc = 0
        if "SCBS&P500A" in selected_funds:
            sp500a_alloc = st.sidebar.slider(
                "SCBS&P500A",
                0.0,
                1.0,
                0.0,
                0.01
            ) 
        else:
            sp500a_alloc = 0
        if "ESGCORE" in selected_funds:
            gcore_alloc = st.sidebar.slider(
                "ESGCORE",
                0.0,
                1.0,
                0.0,
                0.01
            )
        else:
            gcore_alloc = 0
    total_alloc = (
      kkpplus_alloc +
      kkpcash_alloc +
      kfa_alloc +
      ugi_alloc +
      gqg_alloc +
      gtech_alloc +
      eae_alloc +
      ktprecious_alloc +
      rostrum_alloc + 
      gnph_alloc + 
      healthcarea_alloc + 
      propa_alloc + 
      sp500a_alloc +
      gcore_alloc
    )
    st.sidebar.write(
        f"Total Weight: {total_alloc:.2f}"
    )
    if total_alloc > 1:
      st.error("Allocations exceed 100%")
      st.sidebar.error(
          f"Allocated: {total_alloc:.0%}. "
          "Reduce the allocation to 100% or less."
      )
      st.stop()
    if initial_amount * rostrum_alloc < 3000000 and rostrum_alloc != 0:
      st.error("Minimum investment for Rostrum Grand Fund of Funds is 3 million THB")
      st.stop()
    savings_alloc = (
          1 -
            (
              kkpplus_alloc +
              kkpcash_alloc +
              kfa_alloc +
              ugi_alloc +
              gqg_alloc +
              gtech_alloc +
              eae_alloc +
              ktprecious_alloc + 
              rostrum_alloc + 
              gnph_alloc +
              healthcarea_alloc + 
              propa_alloc + 
              sp500a_alloc +
              gcore_alloc
            )
    )
    import pandas as pd
    import plotly.express as px

    allocation_data = pd.DataFrame({
      "Asset": [
          "KKP Plus",
          "KKP Cash",
          "KFAFIX",
          "UGISFX",
          "ESGQG",
          "ESGTECH",
          "ESEAE",
          "KTPRECIOUS",
          "Savings",
          "Rostrum",
          "KKPGNPH",
          "KTHEALTHCAREA",
          "KFGPROPA",
          "SCBS&P500A",
          "ESGCORE"
      ],
    "Allocation": [
          kkpplus_alloc,
          kkpcash_alloc,
          kfa_alloc,
          ugi_alloc,
          gqg_alloc,
          gtech_alloc,
          eae_alloc,
          ktprecious_alloc,
          savings_alloc,
          rostrum_alloc,
          gnph_alloc,
          healthcarea_alloc,
          propa_alloc,
          sp500a_alloc,
          gcore_alloc
      ]
    })

    allocation_data = allocation_data[
      allocation_data["Allocation"] > 0
    ]
    return {name: float(value) for name,value in zip(FUND_NAMES + ['Rostrum'], [ktprecious_alloc, gqg_alloc, eae_alloc, gtech_alloc, gnph_alloc, gcore_alloc, kkpplus_alloc, kkpcash_alloc, kfa_alloc, ugi_alloc, healthcarea_alloc, propa_alloc, sp500a_alloc, rostrum_alloc])}, preset


def original_charts(result, allocation_data):
    import plotly.express as px
    req = result["request"]
    age_years = req["age"]
    acum_years = req["years_until_retirement"]
    ages = np.asarray(result["chart_ages"], dtype=float)
    percentiles = np.asarray([result["percentiles"][str(p)] for p in [10,25,50,75,90]], dtype=float)
    import plotly.graph_objects as go
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
      x=ages,
      y=percentiles[4]/1000000,
      mode='lines',
      name='90th Percentile',
      hovertemplate=
      'Year: %{x:.1f}<br>' +
      'Value: ฿%{y:,.2f}M<extra></extra>'
    ))  

    fig.add_trace(go.Scatter(
      x=ages,
      y=percentiles[3]/1000000,
      mode='lines',
      name='75th Percentile',
      hovertemplate=
      'Year: %{x:.1f}<br>' +
      'Value: ฿%{y:,.2f}M<extra></extra>'
    ))  

    fig.add_trace(go.Scatter(
      x=ages,
      y=percentiles[2]/1000000,
      mode='lines',
      name='50th Percentile',
      hovertemplate=
      'Year: %{x:.1f}<br>' +
      'Value: ฿%{y:,.2f}M<extra></extra>'
    ))  

    fig.add_trace(go.Scatter(
      x=ages,
      y=percentiles[1]/1000000,
      mode='lines',
      name='25th Percentile',
      hovertemplate=
      'Year: %{x:.1f}<br>' +
      'Value: ฿%{y:,.2f}M<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
      x=ages,
      y=percentiles[0]/1000000,
      mode='lines',
      name='10th Percentile',
      hovertemplate=
      'Year: %{x:.1f}<br>' +
      'Value: ฿%{y:,.2f}M<extra></extra>'
    ))

    fig.add_vline(
      x=acum_years+age_years,
      line_dash="dash",
      annotation_text="Retirement",
      line_color = "white"
    )

    fig.add_vline(
        x=85,
        line_dash = "dash",
        annotation_text = "Average Thai Lifespan",
        line_color = "white"
    )

    fig.update_xaxes(
          title_text="Age",
          range = [float(age_years),85]
      )

    fig.update_yaxes(
      title_text="Portfolio Value (Million THB)"
    )

    fig = style_line_chart(
      fig,
      "Nominal Portfolio Value Projection"
    )

    import copy

    mobile_fig = copy.deepcopy(fig)


    mobile_fig.update_layout(
      title=dict(text="",x=0),

      autosize=True,
      height=560,

      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(5,13,27,0.35)",

      margin=dict(
          l=48,
          r=14,
          t=125,
          b=58
      ),

      legend=dict(
          orientation="h",

          x=0.5,
          xanchor="center",

          y=1.19,
          yanchor="top",

          font=dict(
              size=10,
              color="#D9E5F5"
              ),

          bgcolor="rgba(0,0,0,0)",

      # Makes each legend item more compact
          itemwidth=32
      ),

      hovermode="x unified",

      hoverlabel=dict(
          bgcolor="#0D1B31",
          bordercolor="#315989",
          font=dict(
              size=11,
              color="#F1F6FF"
          )
      )
    )
    mobile_fig.update_xaxes(
      range=[
          float(age_years),
          85
        ],

      dtick=10,

      title=dict(
          text="Age",
          font=dict(
              size=12,
              color="#DCE8F8"
          )
      ),

      tickfont=dict(
          size=10,
          color="#A8BAD4"
      ),

      automargin=True,
      showgrid=False,
      zeroline=False
    )

    mobile_fig.update_yaxes(
      nticks=6,

      title=dict(
          text="Portfolio Value<br>(Million THB)",
          font=dict(
              size=11,
              color="#DCE8F8"
          )
      ),

      tickfont=dict(
          size=10,
          color="#A8BAD4"
      ),

      automargin=True,

      gridcolor="rgba(140,180,235,0.13)",
      zeroline=False
    )

    mobile_fig.update_layout(
      annotations=[]
    )

    retirement_age = age_years + acum_years

    mobile_fig.add_annotation(
      x=retirement_age,
      y=1.01,

      xref="x",
      yref="paper",

      text="Retirement",
      showarrow=False,

      xanchor="left",
      yanchor="bottom",

      font=dict(
          size=10,
          color="#D9E5F5"
      )
    )

    mobile_fig.add_annotation(
      x=85,
      y=1.01,

      xref="x",
      yref="paper",

      text="Age 85",
      showarrow=False,

      xanchor="right",
      yanchor="bottom",

      font=dict(
          size=10,
          color="#D9E5F5"
      )
    )

    # Desktop version
    with st.container(key="projection_desktop"):
      st.plotly_chart(
          fig,
          width="stretch",
          key="projection_desktop_chart",
          config={
              "responsive": True,
              "displayModeBar": False
          }
      )


    # Mobile version
    with st.container(key="projection_mobile"):
      st.html("""
      <div class="mobile-chart-heading">
          Nominal Portfolio Value Projection
      </div>
      """)

      st.plotly_chart(
          mobile_fig,
          width="stretch",
          key="projection_mobile_chart",
          config={
              "responsive": True,
              "displayModeBar": False
          }
      )

    pie_fig = px.pie(
      allocation_data,
      names="Asset",
      values="Allocation",
      hole=0.48
      )

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
          text="Portfolio Allocation",
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
      ),

      annotations=[
          dict(
              text="Portfolio<br>Allocation",
              x=0.5,
              y=0.5,
              showarrow=False,
              align="center",
              font=dict(
                  size=15,
                  color="#A8BAD4"
              )
          )
      ]
    )

    st.plotly_chart(
      pie_fig,
      width="stretch",
      config={
          "responsive": True,
          "displayModeBar": False
      }
    )

    import plotly.express as px
    ending_values = np.asarray(result["ending_values"], dtype=float)

    import plotly.graph_objects as go
    ending_values_m = ending_values / 1_000_000
    capped_values = np.minimum(ending_values_m, 120)
    ending_values = np.asarray(result["ending_values"], dtype=float)

    histogram_values = np.minimum(
      ending_values_m,
      250.0
      )

    fig_hist = go.Figure()

    fig_hist.add_trace(
      go.Histogram(
          x=histogram_values,


      xbins=dict(
          start=0,
          end=260,
          size=10
      ),

      marker=dict(
          color="#7DBCF0",
          line=dict(
              color="rgba(5, 16, 32, 0.65)",
              width=1
          )
          ),

      hovertemplate=(
          "Final value: ฿%{x:,.0f}M<br>"
          "Simulations: %{y}"
          "<extra></extra>"
          )
      )
    )

    fig_hist.update_layout(
      title=dict(
          text="Distribution of Final Portfolio Values",
          x=0.01,
          xanchor="left",
          font=dict(
          size=20,
          color="#F1F6FF"
          )
      ),

      xaxis_title="Final Portfolio Value (Million THB)",
      yaxis_title="Number of Simulations",

      height=500,
      bargap=0.04,
      showlegend=False,

      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(5,13,27,0.35)",

      font=dict(
          family="Inter, Arial, sans-serif",
          color="#D9E5F5"
      ),

      margin=dict(
          l=80,
          r=45,
          t=85,
          b=75
      )
    )

    fig_hist.update_xaxes(
      range=[0, 260],

      tickmode="array",
      tickvals=[0, 50, 100, 150, 200, 250],
      ticktext=[
          "0",
          "50",
          "100",
          "150",
          "200",
          "250+"
      ],

      showgrid=False,
      zeroline=False,
      automargin=True
    )

    fig_hist.update_yaxes(
      showgrid=True,
      gridcolor="rgba(140,180,235,0.13)",
      zeroline=False,
      automargin=True
    )

    st.plotly_chart(
      fig_hist,
      width="stretch",
      config={
          "responsive": True,
          "displayModeBar": False
      }
    )


    return fig, pie_fig, fig_hist


with st.container(key="hero_actions"):
    run = st.button(
        "Run Simulation",
        key="run_simulation",
        type="primary",
        icon=":material/arrow_forward:",
        icon_position="right",
        width=240
    )
with st.sidebar:
    initial_amount = thb_number_input(
        label = "Initial Amount",
        min_value = 0,
        max_value = 100000000,
        value = 1000000,
        step = 1000000,
        key = "initial_amount"
    )

    monthly_contribution = thb_number_input(
        label = "Monthly Contribution",
        min_value = 0,
        max_value = 300000,
        value = 10000,
        key = "monthly_contribution"
    )
    withdrawal = thb_number_input(
        label = "Annual Withdrawal",
        min_value = 0,
        max_value = 3000000,
        value = 10000,
        key = "withdrawal"
    )
num_simulations = st.sidebar.slider(
    "Simulations",
    100,
    500,
    250,
    10
)

avg_inflation_rate = st.sidebar.slider(
    "Average Inflation Rate",
    0.0,
    0.15,
    0.02,
    0.01
)
with st.sidebar:
    target = thb_number_input(
        label = "Target Retirement Wealth",
        min_value = 0,
        max_value = 100000000,
        value = 5000000,
        key = "target"
    )

    acum_years = thb_number_input(
        label = "Years Until Retirement",
        min_value = 0,
        max_value = 100,
        value = 1,
        key = "acum_years"
    )

    age_years = thb_number_input(
        label = "Your Age",
        min_value = 0,
        max_value = 100,
        value = 1,
        key = "age_years"
    )

input_data = {
    "Initial Capital" : initial_amount,
    "DCA amount (amount added per month)" : monthly_contribution,
    "Annual Withdrawal" : withdrawal,
    "Number of Simulations" : num_simulations,
    "Target Wealth at Retirement" : target,
    "Current age" : age_years,
    "Years until retirement" : acum_years,
    "Inflation rate" : avg_inflation_rate}


def setting(name, default=''):
    value = os.getenv(name)
    if value is not None:
        return value
    try:
        return str(st.secrets.get(name, default))
    except FileNotFoundError:
        return default


st.sidebar.title('Retirement Simulator')
model_type = st.sidebar.radio('Model Type', [
    'Market Index Based Portfolio Model', 'Bluebell Offered Mutual Funds Model'])
model = 'index' if model_type == 'Market Index Based Portfolio Model' else 'funds'
retirement_years = 85 - (age_years + acum_years)
if retirement_years <= 0:
    st.error('Change your age and retirement years so retirement begins before age 85.')
    st.stop()
weights, preset = index_controls() if model == 'index' else fund_controls()
api_url = setting('SIMULATOR_API_URL').rstrip('/')
api_key = setting('SIMULATOR_API_KEY')

if run:
    started = time.perf_counter()
    try:
        req = SimulationRequest(model=model, age=age_years, years_until_retirement=acum_years,
            initial_amount=initial_amount, monthly_contribution=monthly_contribution,
            annual_withdrawal=withdrawal, target=target, simulations=num_simulations,
            inflation=avg_inflation_rate, weights=weights)
        with st.spinner('Running simulation...'):
            if api_url:
                headers = {'X-API-Key': api_key} if api_key else {}
                with httpx.Client(timeout=httpx.Timeout(180., connect=10.)) as client:
                    response = client.post(api_url + '/api/simulate', json=req.model_dump(), headers=headers)
                    if response.is_error:
                        raise RuntimeError(f"Simulation service ({response.status_code}): {response.json().get('detail', response.text)}")
                    result = response.json()
            else:
                from fast_simulator.engine import simulate
                result = simulate(req)
        st.session_state.fast_result = result
        st.session_state.fast_elapsed = time.perf_counter() - started
        st.session_state.fast_preset = preset
        st.session_state.pop('fast_pdf', None)
    except Exception as exc:
        st.error(str(exc))

result = st.session_state.get('fast_result')
if result:
    req = result['request']
    stats = result['statistics']
    # Results and report always use the completed run, even while inputs are edited.
    allocation = {name: value for name, value in req['weights'].items() if value > 0}
    residual = max(0., 1 - sum(req['weights'].values()))
    if residual:
        allocation['Pure Cash' if result['model'] == 'index' else 'Savings'] = residual
    allocation_data = pd.DataFrame({'Asset': list(allocation), 'Allocation': list(allocation.values())})
    current_inputs = dict(model=model, age=age_years, years_until_retirement=acum_years,
        initial_amount=float(initial_amount), monthly_contribution=float(monthly_contribution),
        annual_withdrawal=float(withdrawal), target=float(target), simulations=num_simulations,
        inflation=avg_inflation_rate, weights=weights)
    if any(req.get(key) != value for key, value in current_inputs.items()):
        st.caption('Showing your last completed simulation. Press Run Simulation to apply edited inputs.')
    fig, pie_fig, fig_hist = original_charts(result, allocation_data)
    c1, c2, c3 = st.columns(3)
    c1.metric('Median Portfolio Value at Retirement', f"฿{stats['median_retirement_wealth']:,.0f}")
    c1.metric('Probability of reaching retirement goal', f"{stats['success_probability']:.1%}")
    c2.metric('Median Ending Portfolio Value (Adjusted for Inflation)', f"฿{stats['median_real_ending_wealth']:,.0f}")
    c2.metric('Portfolio Failure Rate', f"{1 - stats['survival_probability']:.2%}")
    annualized = stats['median_accumulation_annualized_return']
    c3.metric('Median Accumulation Annualized Return', 'N/A' if annualized is None else f'{annualized:.1%}',
        help='Median of daily time-weighted accumulation returns across valid trials, excluding contributions. This uses the corrected per-trial statistic; it is not growth of the percentile line.')
    c3.metric('Median Maximum Drawdown', f"{stats['median_max_drawdown']:.1%}")
    if result.get('sampling_mode') == 'shared_scenarios':
        st.caption('Shared scenarios are reused for stable portfolio comparisons.')
    st.caption(f"Calculation completed in {st.session_state.fast_elapsed:.2f}s. Chart rendering is additional.")
    statistics = {
        'Initial investment': f"THB {req['initial_amount']:,.0f}",
        'Monthly contribution': f"THB {req['monthly_contribution']:,.0f}",
        'Retirement target': f"THB {req['target']:,.0f}",
        'Goal achievement probability': f"{stats['success_probability']:.1%}",
        'Median Wealth at Retirement': f"THB {stats['median_retirement_wealth']:,.0f}",
        'Portfolio failure rate': f"{1 - stats['survival_probability']:.1%}",
        'Inflation-adjusted median value': f"THB {stats['median_real_ending_wealth']:,.0f}",
        'Median maximum drawdown': f"{stats['median_max_drawdown']:.1%}",
        'Median accumulation annualized return': 'N/A' if annualized is None else f'{annualized:.1%}',
        'Assumed Inflation Rate': f"{req['inflation']:.1%}",
    }
    disclaimer = ('This report is generated from a Monte Carlo simulation and is intended for educational and scenario-planning purposes. '
        'The simulation relies on historical data and model assumptions. Actual investment returns, inflation, fees, taxes, withdrawals, '
        'and market conditions may differ materially. The results are not guaranteed and do not constitute individualized financial advice.')
    with c1:
        generate = st.button('Generate Portfolio Report', key='generate_portfolio_report')
    if generate:
        with st.spinner('Preparing report...'):
            try:
                from fast_simulator.original_report import build_portfolio_pdf
                st.session_state.fast_pdf = build_portfolio_pdf(
                    projection_figure=fig, allocation_figure=pie_fig, histogram_figure=fig_hist,
                    statistics=statistics,
                    portfolio_name=st.session_state.get('fast_preset', 'Custom') if result['model'] == 'funds' else 'Custom Market Index Portfolio',
                    disclaimer=disclaimer)
            except Exception:
                # Local installations may not have Chromium. Still provide an export.
                from fast_simulator.report import build_report
                st.session_state.fast_pdf = build_report(result)
                st.info('The original PDF chart renderer is unavailable here; a simplified report was generated.')
    if st.session_state.get('fast_pdf'):
        with c1:
            st.download_button('Download Portfolio Report', st.session_state.fast_pdf,
                file_name='bluebell_portfolio_report.pdf', mime='application/pdf',
                key='download_portfolio_report', type='primary',
                icon=':material/download:', on_click='ignore', width=280)
else:
    st.info('Choose your inputs and allocations, then press Run Simulation.')
