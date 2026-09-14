import sys
from pathlib import Path

# Add warehouseAI project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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

if "username" not in st.session_state:
    st.session_state.username = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# LOGIN PAGE
# ============================================================

def show_login_page():
    """Display the login page."""

    # Center the login box using columns
    left, center, right = st.columns([1, 1.5, 1])

    with center:
        st.markdown(
            "<div style='text-align: center;'>"
            "<h1>🏭 WarehouseAI</h1>"
            "<p>Warehouse Intelligence Platform</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.write("")

        with st.container(border=True):
            st.subheader("Sign in")

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            st.write("")

            login_clicked = st.button(
                "Login",
                type="primary",
                use_container_width=True,
            )

            if login_clicked:

                if username == USERNAME and password == PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.username = username

                    # Start with a fresh conversation
                    st.session_state.history = []
                    st.session_state.messages = []

                    st.rerun()

                else:
                    st.error("Invalid username or password.")

        st.caption("Please sign in to access WarehouseAI.")


# ============================================================
# LOGOUT
# ============================================================

def logout():
    """Log the user out and clear the current conversation."""

    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.history = []
    st.session_state.messages = []

    st.rerun()


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
# SHOW LOGIN OR DASHBOARD
# ============================================================

if not st.session_state.authenticated:

    # User is NOT logged in
    show_login_page()

    # Stop execution here.
    # Nothing below this point will be displayed.
    st.stop()


# ============================================================
# DASHBOARD
# ============================================================

st.title("WarehouseAI")

st.caption(
    "Ask questions about orders, allocation, inventory, movements "
    "and the material handling system/conveyors."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Session")

    st.success(
        f"Logged in as **{st.session_state.username}**"
    )

    if st.button(
        "Logout",
        use_container_width=True,
    ):
        logout()

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


# ============================================================
# WELCOME MESSAGE
# ============================================================

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


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        show_tool_trace(
            message.get("tool_trace", [])
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a warehouse question…"
)


if question:

    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)


    # --------------------------------------------------------
    # Generate assistant response
    # --------------------------------------------------------

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


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Built with :material/warehouse: WarehouseAI | "
    "Powered by OpenAI & ChromaDB"
)
