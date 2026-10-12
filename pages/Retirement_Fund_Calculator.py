from datetime import date
import streamlit as st
from pathlib import Path

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Retirement Lifestyle Investigator",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="auto",
)
from collections.abc import Callable
from typing import Any

import streamlit as st


import html
from collections.abc import Callable
from typing import Any
import streamlit as st

st.html(Path("style.css"))
from button import thb_number_input, load_thb_input_styles
load_thb_input_styles()
st.title("Retirement Funds Calculator")
col1, col2, col3 = st.columns(3)
st.write("ประเมินค่าใช้จ่ายแต่ละประเภทต่อเดือน")
with col1:
    household = thb_number_input(label = "ค่าใช้จ่ายเกี่ยวกับบ้าน", min_value = 0, key = "household")
    bills = thb_number_input (label = "ค่าสาธารณูปโภค (ค่าไฟฟ้า, ค่าน้ำประปา, อื่น ๆ)" , min_value = 0, key = "bills")
    leisure = thb_number_input (label = "ค่าท่องเที่ยว/สันทนาการ", min_value = 0, key = "leisure")
    other = thb_number_input(label = "ค่าใช้จ่ายอื่น ๆ", min_value = 0, key = "other")
with col2:
    Food_and_dining = thb_number_input (label = "ค่าใช้จ่ายเกี่ยวกับอาหาร", min_value = 0, key = "Food_and_dining" )
    clothes = thb_number_input (label = "ค่าเสื้อผ้า เครื่องแต่งกาย", min_value = 0, key = "clothes" )
    travel = thb_number_input (label = "ค่าเดินทาง", min_value = 0, key = "travel" )
    donate = thb_number_input(label = "ค่าบริจาค/ทำบูญ", min_value = 0, key = "donate" )
with col3:
    hospital = thb_number_input (label = "ค่าใช้จ่ายเกี่ยวกับสุขภาพ",min_value = 0, key = "hospital" )
    rent = thb_number_input (label = "ค่าผ่อนบ้าน/ผ่อนรถ", min_value = 0, key = "rent")
    child = thb_number_input(label = "ค่าเลี้ยงลูกหลาน", min_value =0, key = "child" )

inf_rate = st.slider(
    "Inflation Rate",
    0.0,
    0.15,
    0.02)
years = st.slider(
    "Years Until Retirement",
    0,
    100,
    15)
sum = (household + bills + leisure +other + Food_and_dining + clothes + travel + donate + hospital + rent + child) * 12
inf_sum = sum * ((1+inf_rate) **years)
c1,c2 = st.columns(2)
c1.metric("ค่าใช้จ่ายต่อปี (Nominal)", value = f"THB{sum:,}")

c2.metric("ค่าใช้จ่ายต่อปี(Inflation Adjusted)", value=f"THB{inf_sum:,.0f}") 
