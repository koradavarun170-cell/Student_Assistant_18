import os
import uuid
import requests
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration & Styling
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMind | Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling adhering to StudyMind Warm Minimalist Palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Global Background and text tones */
    .stApp {
        background-color: #F8F5F1;
    }
    
    /* Header brand */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid #E4DDD6;
        margin-bottom: 16px;
    }
    .brand-icon {
        width: 38px;
        height: 38px;
        background: #1A1612;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        color: white;
    }
    .brand-title {
        font-size: 17px;
        font-weight: 700;
        color: #1A1612;
        line-height: 1.2;
    }
    .brand-sub {
        font-size: 12px;
        color: #6B5F54;
    }
    
    /* Status pills */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    .status-connected {
        background: #EAF7EC;
        border: 1px solid #BBDFC8;
        color: #16A34A;
    }
    .status-disconnected {
        background: #FDF0F0;
        border: 1px solid #F5BFBF;
        color: #DC2626;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
    }
    .status-dot-green { background-color: #16A34A; }
    .status-dot-red { background-color: #DC2626; }
    
    /* Source badges */
    .source-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        background: #EEF4FF;
        border: 1px solid #BFCFEF;
        border-radius: 16px;
        font-size: 11px;
        color: #2563EB;
        font-weight: 500;
        margin: 2px 4px 2px 0;
    }
    
    /* File badge types */
    .file-badge {
        display: inline-block;
        font-size: 9px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .badge-pdf { background: #FDE8E8; color: #DC2626; border: 1px solid #F5BFBF; }
    .badge-docx, .badge-doc { background: #EEF4FF; color: #2563EB; border: 1px solid #BFCFEF; }
    .badge-pptx, .badge-ppt { background: #FEF3C7; color: #B45309; border: 1px solid #EDD5A3; }
    
    /* Welcome cards */
    .welcome-card {
        background: #FFFFFF;
        border: 1px solid #E4DDD6;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state["user_id"] = "student_" + str(uuid.uuid4())[:6]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

if "pending_question" not in st.session_state:
    st.session_state["pending_question"] = None

# Backend API Configuration
DEFAULT_API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
if "api_url" not in st.session_state:
    st.session_state["api_url"] = DEFAULT_API_URL


def check_backend_health(base_url):
    try:
        r = requests.get(f"{base_url}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class="brand-container">
            <div class="brand-icon">📚</div>
            <div>
                <div class="brand-title">StudyMind</div>
                <div class="brand-sub">Document AI Assistant (LangGraph)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Session ID Management
    st.markdown("##### 👤 Session Identification")
    user_id_input = st.text_input(
        "Session ID / User ID",
        value=st.session_state["user_id"],
        help="All documents and memory are scoped to this unique session ID."
    )
    if user_id_input != st.session_state["user_id"]:
        st.session_state["user_id"] = user_id_input.strip()

    # Connection Status
    is_online = check_backend_health(st.session_state["api_url"])
    if is_online:
        st.markdown("""
            <div class="status-badge status-connected">
                <span class="status-dot status-dot-green"></span>
                <span>Backend Online</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="status-badge status-disconnected">
                <span class="status-dot status-dot-red"></span>
                <span>Backend Offline</span>
            </div>
        """, unsafe_allow_html=True)

    with st.expander("⚙️ Backend API Settings", expanded=False):
        custom_url = st.text_input(
            "FastAPI URL",
            value=st.session_state["api_url"],
            help="Set to your local or deployed Render URL (e.g. https://student-assistant-api.onrender.com)"
        )
        if custom_url != st.session_state["api_url"]:
            st.session_state["api_url"] = custom_url.rstrip("/")
            st.rerun()

    st.markdown("---")

    # Document Tabs: Upload & Manage
    tab_upload, tab_manage = st.tabs(["⬆️ Upload", "📂 Manage"])

    # ── Upload Tab ──
    with tab_upload:
        st.caption("Supported formats: PDF, DOCX, DOC, PPTX, PPT")
        uploaded_files_stage = st.file_uploader(
            "Select files",
            type=["pdf", "docx", "doc", "pptx", "ppt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if uploaded_files_stage:
            st.markdown(f"**{len(uploaded_files_stage)} file(s) selected:**")
            for f in uploaded_files_stage:
                ext = f.name.split(".")[-1].lower()
                badge_class = f"badge-{ext}" if ext in ["pdf", "docx", "doc", "pptx", "ppt"] else "badge-pdf"
                st.markdown(
                    f"<span class='file-badge {badge_class}'>{ext}</span> <small>{f.name}</small>",
                    unsafe_allow_html=True
                )

            if st.button("🚀 Upload & Process", type="primary", use_container_width=True):
                if not st.session_state["user_id"].strip():
                    st.error("Please enter a Session ID first.")
                else:
                    with st.spinner("Extracting text, chunking & generating embeddings..."):
                        try:
                            files_payload = [
                                ("files", (file.name, file.getvalue(), file.type or "application/octet-stream"))
                                for file in uploaded_files_stage
                            ]
                            data_payload = {"user_id": st.session_state["user_id"]}
                            
                            response = requests.post(
                                f"{st.session_state['api_url']}/upload",
                                data=data_payload,
                                files=files_payload,
                                timeout=120
                            )

                            if response.status_code == 200:
                                for file in uploaded_files_stage:
                                    if file.name not in st.session_state["uploaded_files"]:
                                        st.session_state["uploaded_files"].append(file.name)
                                st.success(f"Successfully processed {len(uploaded_files_stage)} document(s)!")
                            else:
                                err_msg = response.json().get("detail", response.text)
                                st.error(f"Upload failed: {err_msg}")
                        except Exception as e:
                            st.error(f"Connection error: {str(e)}")

    # ── Manage Tab ──
    with tab_manage:
        st.caption("Active documents for this session:")
        if not st.session_state["uploaded_files"]:
            st.info("No documents uploaded yet in this session.")
        else:
            to_remove = None
            for fname in st.session_state["uploaded_files"]:
                ext = fname.split(".")[-1].lower()
                badge_class = f"badge-{ext}" if ext in ["pdf", "docx", "doc", "pptx", "ppt"] else "badge-pdf"
                
                col_name, col_btn = st.columns([0.75, 0.25])
                with col_name:
                    st.markdown(f"<span class='file-badge {badge_class}'>{ext}</span> <small>{fname}</small>", unsafe_allow_html=True)
                with col_btn:
                    if st.button("🗑️", key=f"del_{fname}", help=f"Delete {fname}"):
                        to_remove = fname

            if to_remove:
                with st.spinner(f"Removing {to_remove}..."):
                    try:
                        resp = requests.delete(
                            f"{st.session_state['api_url']}/delete",
                            json={"user_id": st.session_state["user_id"], "filename": to_remove},
                            timeout=30
                        )
                        if resp.status_code == 200:
                            st.session_state["uploaded_files"].remove(to_remove)
                            st.success(f"Deleted {to_remove}")
                            st.rerun()
                        else:
                            st.error("Failed to delete document from vector index.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        st.markdown("---")
        if st.button("🧹 Clear Chat History", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Main Chat Area
# ─────────────────────────────────────────────────────────────────────────────
st.title("📚 StudyMind Document Assistant")
st.caption(f"Connected to LangGraph RAG Agent | Active Session: `{st.session_state['user_id']}`")

# Empty State / Starter Suggestions
if len(st.session_state["messages"]) == 0:
    st.markdown("""
        <div class="welcome-card">
            <h3>Welcome to your Study Assistant!</h3>
            <p style="color: #6B5F54; max-width: 580px; margin: 0 auto 16px auto;">
                Upload your study materials (lecture slides, textbooks, or class notes) in the sidebar.
                Ask any question, and the assistant will retrieve grounded answers with direct citations.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 💡 Suggested Questions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📌 Summarize the key concepts", use_container_width=True):
            st.session_state["pending_question"] = "Summarize the key concepts from the uploaded documents."
            st.rerun()
        if st.button("📐 Explain core definitions and formulas", use_container_width=True):
            st.session_state["pending_question"] = "What are the core definitions and formulas covered in this material?"
            st.rerun()
    with col2:
        if st.button("❓ Create 3 practice quiz questions", use_container_width=True):
            st.session_state["pending_question"] = "Create 3 practice quiz questions with detailed answers based on my documents."
            st.rerun()
        if st.button("🔍 Detail the main methodology or arguments", use_container_width=True):
            st.session_state["pending_question"] = "Detail the main methodology or key arguments presented in the files."
            st.rerun()

# Display Chat History
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.markdown("<div style='margin-top: 8px;'><b>Sources:</b></div>", unsafe_allow_html=True)
            sources_html = ""
            for s in msg["sources"]:
                file_name = s.get("file", "Unknown Document")
                page_num = s.get("page", "N/A")
                sources_html += f"<span class='source-chip'>📄 {file_name} (Page {page_num})</span> "
            st.markdown(sources_html, unsafe_allow_html=True)

# Handle Input: either from chat_input or a clicked suggestion
user_input = st.chat_input("Ask a question about your study material...")
prompt_to_send = None

if user_input:
    prompt_to_send = user_input
elif st.session_state["pending_question"]:
    prompt_to_send = st.session_state["pending_question"]
    st.session_state["pending_question"] = None

if prompt_to_send:
    user_id = st.session_state["user_id"].strip()
    if not user_id:
        st.error("Please specify a Session ID in the sidebar before asking questions.")
    else:
        # Add user query to conversation history
        st.session_state["messages"].append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)

        # Assistant thinking & LangGraph RAG execution
        with st.chat_message("assistant"):
            with st.spinner("Searching documents & generating answer with LangGraph..."):
                try:
                    payload = {"user_id": user_id, "question": prompt_to_send}
                    response = requests.post(
                        f"{st.session_state['api_url']}/query",
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer received.")
                        sources = data.get("sources", [])

                        st.markdown(answer)
                        if sources:
                            st.markdown("<div style='margin-top: 8px;'><b>Sources:</b></div>", unsafe_allow_html=True)
                            sources_html = ""
                            for s in sources:
                                file_name = s.get("file", "Unknown Document")
                                page_num = s.get("page", "N/A")
                                sources_html += f"<span class='source-chip'>📄 {file_name} (Page {page_num})</span> "
                            st.markdown(sources_html, unsafe_allow_html=True)

                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                    else:
                        detail = response.json().get("detail", response.text)
                        err_msg = f"⚠️ **Could not process query:** {detail}"
                        st.markdown(err_msg)
                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": err_msg
                        })
                except Exception as e:
                    err_text = f"⚠️ **Connection error:** Could not reach backend at `{st.session_state['api_url']}`. Make sure the FastAPI server is running."
                    st.markdown(err_text)
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": err_text
                    })
