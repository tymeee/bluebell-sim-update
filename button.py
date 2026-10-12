import streamlit as st
import html
from textwrap import dedent
from collections.abc import Callable
from typing import Any

def load_thb_input_styles() -> None:
    st.markdown(
        """
<style>
/* ======================================================
   THB NUMBER INPUT
   Load this after every other CSS block
   ====================================================== */

div[class*="st-key-thb_input_"] {
    margin-bottom: 1rem;
}

/* Header */
div[class*="st-key-thb_input_"] .thb-input-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.65rem;

    margin-bottom: 0.45rem;
}

div[class*="st-key-thb_input_"] .thb-input-label {
    color: #f1f6ff;

    font-size: 0.92rem;
    font-weight: 600;
    line-height: 1.35;
}

div[class*="st-key-thb_input_"] .thb-input-label-hidden {
    visibility: hidden;
}

div[class*="st-key-thb_input_"] .thb-input-badge {
    flex-shrink: 0;

    padding: 0.12rem 0.42rem;

    border: 1px solid rgba(125, 165, 210, 0.20);
    border-radius: 999px;

    background: rgba(78, 125, 180, 0.10);
    color: #91b8e7;

    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
}

/* Control row */
div[class*="st-key-thb_input_"]
[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 0.45rem !important;
}

div[class*="st-key-thb_input_"]
[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Remove default button spacing */
div[class*="st-key-thb_input_"] .stButton {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    width: 100% !important;

    margin: 0 !important;
    padding: 0 !important;
}

/* Custom THB component wrapper */
div[class*="st-key-thb_input_"] {
    margin-bottom: 1rem;
}

/* Header */
div[class*="st-key-thb_input_"] .thb-input-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.45rem;
}

div[class*="st-key-thb_input_"] .thb-input-label {
    color: #f1f6ff;
    font-size: 0.92rem;
    font-weight: 600;
}

div[class*="st-key-thb_input_"] .thb-input-badge {
    padding: 0.13rem 0.43rem;
    border: 1px solid rgba(113, 163, 220, 0.25);
    border-radius: 999px;
    background: rgba(79, 140, 255, 0.09);
    color: #91b8e7;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
}

/* Three-control row */
div[class*="st-key-thb_input_"]
[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 0.45rem !important;
}

/* Style every button inside this component.
   There are only the minus and plus buttons here. */
div[class*="st-key-thb_input_"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
}

div[class*="st-key-thb_input_"] .stButton > button {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    width: 100% !important;
    height: 44px !important;
    min-height: 44px !important;

    margin: 0 !important;
    padding: 0 !important;

    border: 1px solid #31516f !important;
    border-radius: 11px !important;

    background: #10243a !important;
    background-color: #10243a !important;
    background-image: none !important;

    color: #91b8e7 !important;

    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.035),
        0 4px 10px rgba(0, 0, 0, 0.12) !important;

    filter: none !important;
    transform: none !important;

    font-size: 1rem !important;
    font-weight: 500 !important;
    line-height: 1 !important;
}

/* Streamlit wraps the button text in several elements */
div[class*="st-key-thb_input_"] .stButton > button > div,
div[class*="st-key-thb_input_"] .stButton > button p,
div[class*="st-key-thb_input_"] .stButton > button span,
div[class*="st-key-thb_input_"]
.stButton
[data-testid="stMarkdownContainer"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    width: 100% !important;
    height: 100% !important;

    margin: 0 !important;
    padding: 0 !important;

    color: inherit !important;
    line-height: 1 !important;
}

div[class*="st-key-thb_input_"] .stButton > button p {
    transform: translateY(-1px);
}

div[class*="st-key-thb_input_"] .stButton > button:hover {
    border-color: #527da8 !important;
    background: #17304b !important;
    background-color: #17304b !important;
    background-image: none !important;
    color: #ffffff !important;
    filter: none !important;
    transform: none !important;
}

div[class*="st-key-thb_input_"] .stButton > button:active {
    transform: scale(0.96) !important;
}

div[class*="st-key-thb_input_"] .stButton > button:disabled {
    border-color: rgba(49, 81, 111, 0.5) !important;
    background: rgba(16, 36, 58, 0.62) !important;
    background-image: none !important;
    color: rgba(145, 184, 231, 0.38) !important;
    opacity: 1 !important;
}

/* Text input */
div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] input {
    height: 44px !important;
    min-height: 44px !important;

    padding: 0 0.95rem !important;

    border: 1px solid #31516f !important;
    border-radius: 11px !important;

    background: #10243a !important;
    color: #f3f7fc !important;

    font-size: 0.94rem !important;
    font-weight: 550 !important;
    font-variant-numeric: tabular-nums !important;

    box-shadow:
        inset 0 1px 1px rgba(0, 0, 0, 0.17),
        0 4px 10px rgba(0, 0, 0, 0.10) !important;
}

/* Input field */
div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] {
    margin: 0 !important;
}

div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] > div {
    margin: 0 !important;
}

div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] input {
    height: 44px !important;
    min-height: 44px !important;

    padding: 0 0.95rem !important;

    border: 1px solid #31516f !important;
    border-radius: 11px !important;

    background: #10243a !important;
    background-color: #10243a !important;
    background-image: none !important;

    color: #f3f7fc !important;

    box-shadow:
        inset 0 1px 1px rgba(0, 0, 0, 0.17),
        0 4px 10px rgba(0, 0, 0, 0.10) !important;

    font-size: 0.94rem !important;
    font-weight: 550 !important;
    font-variant-numeric: tabular-nums !important;

    outline: none !important;
}

div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] input:hover {
    border-color: #456b91 !important;
}

div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] input:focus {
    border-color: #6394c6 !important;

    background: #122a44 !important;
    background-color: #122a44 !important;

    box-shadow:
        0 0 0 3px rgba(99, 148, 198, 0.12),
        inset 0 1px 1px rgba(0, 0, 0, 0.13) !important;
}

/* Help */
div[class*="st-key-thb_input_"] .thb-input-help {
    margin: 0.4rem 0 0;

    color: #8194ad;

    font-size: 0.73rem;
    line-height: 1.4;
}

/* Slightly tighter sidebar version */
[data-testid="stSidebar"]
div[class*="st-key-thb_input_"]
div[class*="__minus"]
button,

[data-testid="stSidebar"]
div[class*="st-key-thb_input_"]
div[class*="__plus"]
button {
    width: 40px !important;
    min-width: 40px !important;
    max-width: 40px !important;

    height: 42px !important;
    min-height: 42px !important;
    max-height: 42px !important;
}

[data-testid="stSidebar"]
div[class*="st-key-thb_input_"]
[data-testid="stTextInput"] input {
    height: 42px !important;
    min-height: 42px !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

def thb_number_input(
    label: str,
    *,
    min_value: int | None = None,
    max_value: int | None = None,
    value: int = 0,
    step: int = 1_000,
    key: str,
    help: str | None = None,
    disabled: bool = False,
    label_visibility: str = "visible",
    on_change: Callable[..., Any] | None = None,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
) -> int:
    """
    Integer input with comma formatting and number-input-style controls.
    """

    if kwargs is None:
        kwargs = {}

    numeric_key = key
    display_key = f"{key}__display"
    minus_key = f"{key}__minus"
    plus_key = f"{key}__plus"
    wrapper_key = f"thb_input_{key}"

    def clamp(number: int) -> int:
        if min_value is not None:
            number = max(number, min_value)

        if max_value is not None:
            number = min(number, max_value)

        return number

    def run_external_callback() -> None:
        if on_change is not None:
            on_change(*args, **kwargs)

    def format_display() -> None:
        raw_value = str(
            st.session_state.get(display_key, "")
        )

        cleaned_value = (
            raw_value
            .replace(",", "")
            .replace("THB", "")
            .replace("฿", "")
            .replace(" ", "")
            .strip()
        )

        try:
            number = int(float(cleaned_value))
            number = clamp(number)

        except (TypeError, ValueError):
            number = int(
                st.session_state.get(
                    numeric_key,
                    value,
                )
            )

        st.session_state[numeric_key] = number
        st.session_state[display_key] = f"{number:,}"

        run_external_callback()

    def decrease_value() -> None:
        current = int(
            st.session_state.get(
                numeric_key,
                value,
            )
        )

        updated = clamp(current - step)

        st.session_state[numeric_key] = updated
        st.session_state[display_key] = f"{updated:,}"

        run_external_callback()

    def increase_value() -> None:
        current = int(
            st.session_state.get(
                numeric_key,
                value,
            )
        )

        updated = clamp(current + step)

        st.session_state[numeric_key] = updated
        st.session_state[display_key] = f"{updated:,}"

        run_external_callback()

    # Initialize the internal numeric value.
    if numeric_key not in st.session_state:
        starting_value = clamp(int(value))
        st.session_state[numeric_key] = starting_value

    # Initialize the visible comma-formatted value.
    if display_key not in st.session_state:
        st.session_state[display_key] = (
            f"{st.session_state[numeric_key]:,}"
        )

    safe_label = html.escape(label)

    with st.container(key=wrapper_key):
        hidden_class = ""
        if label_visibility != "collapsed":
            hidden_class = (
                " thb-input-label-hidden"
                if label_visibility == "hidden"
                else ""
                )    
        st.markdown(
            f"""
            <div class="thb-input-header">
            <span class="thb-input-label{hidden_class}">{safe_label}</span>
            <span class="thb-input-badge">THB</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


        minus_column, input_column, plus_column = st.columns(
            [0.72, 5.8, 0.72],
            gap="small",
            vertical_alignment="center",
        )

        with minus_column:
            st.button(
                "−",
                key=minus_key,
                on_click=decrease_value,
                disabled=(
                    disabled
                    or (
                        min_value is not None
                        and st.session_state[numeric_key]
                        <= min_value
                    )
                ),
                use_container_width=True,
            )

        with input_column:
            st.text_input(
                label,
                key=display_key,
                on_change=format_display,
                disabled=disabled,
                label_visibility="collapsed",
                placeholder="0",
            )

        with plus_column:
            st.button(
                "+",
                key=plus_key,
                on_click=increase_value,
                disabled=(
                    disabled
                    or (
                        max_value is not None
                        and st.session_state[numeric_key]
                        >= max_value
                    )
                ),
                use_container_width=True,
            )

        if help:
            st.markdown(
                dedent(
                    f"""
                    <p class="thb-input-help">
                        {html.escape(help)}
                    </p>
                    """
                    ),
                unsafe_allow_html=True,
            )

    return int(st.session_state[numeric_key])
