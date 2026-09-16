import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import streamlit as st
from openai import OpenAI

from agents.warehouse_chat import run_chat_turn
from ui.core.rag.retrieve import format_chunks_for_context

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="WarehouseAI",
    page_icon=":material/warehouse:",
    layout="wide",
)
# ============================================================
# LOGIN CONFIGURATION
# ============================================================

USERNAME = "admin"
PASSWORD = "admin"

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_display_name" not in st.session_state:
    st.session_state.user_display_name = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# LOGIN PAGE
# ============================================================
def show_login_page():
    """Display the login page."""

    st.markdown("""
    <style>

    /* ========================================================
       PAGE
       ======================================================== */

    .stApp {
        background: linear-gradient(
            135deg,
            #0a2540 0%,
            #1e3a5f 100%
        );
    }

    /* Reduce Streamlit's default top spacing */
    .block-container {
        padding-top: 4rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Hide Streamlit chrome */
    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* ========================================================
       LEFT BRANDING
       ======================================================== */

    .subtitle-text {
        color: #64b5f6;
        font-size: 0.9rem;
        letter-spacing: 2px;
        font-weight: 600;
        margin: 0 0 1.5rem 0;
    }

    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        line-height: 1.1;
    }

    .warehouse-text {
        color: white;
    }
    .username {
            color: white;
        }
        .passwordb {
                color: white;
            }

    .ai-text {
        color: #ff6b35;
    }

    .tagline {
        color: #64b5f6;
        font-size: 1.2rem;
        margin: 0 0 2rem 0;
        font-weight: 500;
    }

    .description {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        line-height: 1.6;
        max-width: 540px;
    }


    /* ========================================================
       LOGIN CARD
       ======================================================== */

    /* This targets the native st.container(border=True) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white;
        border: none !important;
        border-radius: 18px;
        padding: 2.5rem 3rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.30);
    }

    .platform-title {
        color: #4a5568;
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0 0 1.5rem 0;
        text-align: center;
    }

    .signin-title {
        color: #1a202c;
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 1.5rem 0;
        text-align: center;
    }


    /* ========================================================
       FORM LABELS
       ======================================================== */

    .stTextInput label {
        color: #2d3748 !important;
        font-weight: 500 !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #cbd5e0;
        background: #f8fafc;
        color: #1a202c;
        padding: 0.75rem 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #0066cc;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }


    /* ========================================================
       LOGIN BUTTON
       ======================================================== */

    .stButton > button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(
            135deg,
            #0066cc 0%,
            #004c99 100%
        );
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(
            135deg,
            #0052a3 0%,
            #003d7a 100%
        );
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.35);
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer-text {
        color: #718096;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 1.5rem;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 900px) {

        .block-container {
            padding: 2rem 1.5rem;
        }

        .main-title {
            font-size: 2.5rem;
        }

        .description {
            max-width: 100%;
        }

    }

    </style>
    """, unsafe_allow_html=True)


    # ========================================================
    # LOGIN LAYOUT
    # ========================================================

    col1, col2 = st.columns(
        [1.15, 0.85],
        gap="large",
        vertical_alignment="center",
    )


    # ========================================================
    # LEFT SIDE
    # ========================================================

    with col1:

        st.markdown(
            '<p class="subtitle-text">'
            'INTELLIGENT WAREHOUSE OPERATIONS'
            '</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h1 class="main-title">'
            '<span class="warehouse-text">Warehouse</span>'
            '<span class="ai-text">AI</span>'
            '</h1>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="tagline">'
            'Intelligent Warehouse Operations Assistant'
            '</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<p class="description">'
            'Transforming warehouse management with AI-powered '
            'insights — ask in plain English, get evidence-backed '
            'answers in seconds.'
            '</p>',
            unsafe_allow_html=True,
        )


    # ========================================================
    # RIGHT SIDE
    # ========================================================

    with col2:

        # IMPORTANT:
        # Use Streamlit's native container instead of an HTML div.
        with st.container(border=True):

            st.markdown(
                '<p class="platform-title">'
                'Warehouse Intelligence Platform'
                '</p>',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<h2 class="signin-title">Sign in</h2>',
                unsafe_allow_html=True,
            )

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password",
            )

            if st.button(
                "Login",
                use_container_width=True,
                key="login_button",
            ):

                if username == USERNAME and password == PASSWORD:

                    st.session_state.authenticated = True
                    st.session_state.user_display_name = username
                    # Start with a fresh conversation
                    st.session_state.history = []
                    st.session_state.messages = []
                    st.success(
                        "Login successful! Redirecting..."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password"
                    )

            st.markdown(
                '<p class="footer-text">'
                'Please sign in to access WarehouseAI.'
                '</p>',
                unsafe_allow_html=True,
            )

# ============================================================
# TOOL TRACE
# ============================================================

def show_tool_trace(tool_trace: list) -> None:
    """Show a compact record of the live WMS checks behind an answer."""

    if not tool_trace:
        return

    with st.expander("Data checked", expanded=False):

        for step in tool_trace:

            arguments = ", ".join(
                f"{key}={value}"
                for key, value in step["arguments"].items()
            )

            # Add icon based on tool type
            tool_icon = ":material/search:"

            if "order" in step["tool"]:
                tool_icon = ":material/list_alt:"

            elif "inventory" in step["tool"]:
                tool_icon = ":material/inventory:"

            elif "movement" in step["tool"]:
                tool_icon = ":material/local_shipping:"

            elif "knowledge" in step["tool"]:
                tool_icon = ":material/description:"

            st.caption(
                f"{tool_icon} `{step['tool']}` "
                f"({arguments}) → **{step['status']}**"
            )

            workflow_trace = step.get("workflow_trace", [])

            for workflow_step in workflow_trace:
                st.caption(f"  ↳ {workflow_step}")

            # Show knowledge retrieval details
            if (
                step["tool"] == "retrieve_knowledge"
                and step.get("status") == "FOUND"
            ):
                st.caption(
                    f"  ↳ Retrieved "
                    f"{step.get('chunk_count', 0)} relevant documents"
                )

# ============================================================
# MAIN APP
# ============================================================

def show_main_app():
    """Display the main warehouse chat application."""
    
    st.title("WarehouseAI")

    st.caption(
        "Ask questions about orders, allocation, inventory, movements "
        "and the material handling system/conveyors."
    )

    # SIDEBAR
    with st.sidebar:

        st.header("Session")

        st.success(
            f"Logged in as **{st.session_state.user_display_name}**"
        )

        if st.button(
            "Logout",
            use_container_width=True,
        ):
            st.session_state.authenticated = False
            st.session_state.user_display_name = ""
            st.session_state.history = []
            st.session_state.messages = []
            st.rerun()

        st.divider()

        if st.button(
            "Clear conversation",
            use_container_width=True,
        ):
            st.session_state.history = []
            st.session_state.messages = []
            st.rerun()

        st.caption(
            "This chat uses live WMS data and keeps its conversation "
            "memory only while this browser session is open."
        )

        st.divider()

        st.subheader("Available data")

        st.markdown(
            """
- :material/list_alt: Order details
- :material/assignment: Allocation status
- :material/inventory: Item inventory
- :material/dashboard: Inventory overview
- :material/local_shipping: Warehouse movements
- :material/description: Knowledge base (SOPs, procedures)
"""
        )

    # WELCOME MESSAGE
    if not st.session_state.messages:

        with st.container(border=True):

            st.markdown(
                """
                :material/waving_hand: Welcome to WarehouseAI! I can help you with:

                - **Live warehouse data**: Orders, inventory, movements, allocation
                - **Knowledge base**: SOPs, procedures, logistics documentation
                - **Shortage investigation**: Root cause analysis for allocation issues

                Try asking:

                > "What are the logistics procedures for inbound operations?"
                """
            )

    # CHAT HISTORY
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            show_tool_trace(
                message.get("tool_trace", [])
            )

    # CHAT INPUT
    question = st.chat_input(
        "Ask a warehouse question…"
    )

    if question:

        # Add user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        # Generate assistant response
        with st.chat_message("assistant"):

            with st.spinner("Processing your request..."):

                tool_trace = []

                try:

                    client = OpenAI()

                    answer = run_chat_turn(
                        client=client,
                        history=st.session_state.history,
                        question=question,
                        tool_trace=tool_trace,
                    )

                    st.markdown(answer)

                    show_tool_trace(tool_trace)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "tool_trace": tool_trace,
                        }
                    )

                except Exception as error:

                    error_message = (
                        f"Unable to complete the request: {error}"
                    )

                    st.error(error_message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                            "tool_trace": tool_trace,
                        }
                    )

    # FOOTER
    st.divider()

    st.caption(
        "Built with :material/warehouse: WarehouseAI | "
        "Powered by OpenAI & ChromaDB"
    )

# ============================================================
# MAIN ROUTING
# ============================================================

if not st.session_state.authenticated:
    show_login_page()
else:
    show_main_app()