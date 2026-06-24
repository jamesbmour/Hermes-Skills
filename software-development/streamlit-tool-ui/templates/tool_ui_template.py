#!/usr/bin/env python3
"""
Streamlit Tool UI Template — Copy and customize for any Python tool/library.

This template wraps an async Python function with:
- Sidebar with engine selection and global options
- Main area with configurable parameters (columns, expanders, dropdowns)
- Async execution with progress bar
- Tabbed result viewer (output, raw, links, metadata)
- Download/export (single file, save-all, ZIP archive)
- Session state history

Usage:
  streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

Customize:
  1. Replace TOOL_NAME, TOOL_DESCRIPTION
  2. Replace run_tool() with your async function
  3. Replace render_config() form fields with your tool's options
  4. Adjust render_results() tabs for your output format
"""

import asyncio
import io
import os
import zipfile
from datetime import datetime

import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Tool Name Web App",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE
# ============================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "current_results" not in st.session_state:
    st.session_state.current_results = None
if "last_config" not in st.session_state:
    st.session_state.last_config = {}

# ============================================================
# DEPENDENCY DETECTION
# ============================================================
@st.cache_data
def check_optional_deps():
    """Detect optional dependencies and return (available, message)."""
    try:
        # Replace with your optional dependency
        import some_optional_lib
        return True, "OK"
    except ImportError:
        return False, "Optional dependency not installed. Using fallback mode."


DEPS_AVAILABLE, DEPS_MSG = check_optional_deps()


# ============================================================
# CORE TOOL FUNCTION (replace with your logic)
# ============================================================

async def run_tool(url, opts, progress_callback=None):
    """
    Replace this with your actual tool logic.
    Should be async and accept a progress_callback(done, total, current).
    Returns a list of result objects.
    """
    results = []
    # Simulate work
    for i in range(3):
        await asyncio.sleep(0.5)
        results.append({
            "url": f"{url}/page{i}",
            "title": f"Page {i}",
            "content": f"Content of page {i}...",
            "success": True,
        })
        if progress_callback:
            progress_callback(i + 1, 3, f"{url}/page{i}")
    return results


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🔧 Tool Name")
        st.caption("Short description of what this tool does")

        # Engine selection
        if DEPS_AVAILABLE:
            engine = st.radio(
                "Engine",
                ["Full Mode", "Fallback Mode"],
                help="Full mode uses optional deps. Fallback is simpler but limited."
            )
        else:
            engine = "Fallback Mode"
            st.warning(f"⚠️ Full mode unavailable: {DEPS_MSG}")

        st.divider()

        # Output directory
        output_dir = st.text_input(
            "Output Directory",
            value="/workspace/output",
            help="Where to save output files"
        )
        os.makedirs(output_dir, exist_ok=True)

        st.divider()

        # History
        if st.session_state.history:
            st.markdown("### Recent Runs")
            for entry in reversed(st.session_state.history[-5:]):
                st.caption(f"`{entry['time']}` — {entry['count']} results")

        return engine, output_dir


# ============================================================
# CONFIG FORM
# ============================================================

def render_config():
    st.markdown("### ⚙️ Configuration")

    col1, col2 = st.columns(2)

    with col1:
        url = st.text_input("🌐 URL", placeholder="https://example.com")
        mode = st.selectbox("Mode", ["mode_a", "mode_b", "mode_c"],
                            help="Select processing mode")

    with col2:
        timeout = st.number_input("Timeout (ms)", 5000, 120000, 30000, step=5000)
        cache_mode = st.selectbox("Cache", ["BYPASS", "ENABLED", "DISABLED"])

    # Advanced options
    with st.expander("🔧 Advanced Options"):
        adv1, adv2 = st.columns(2)
        with adv1:
            flag1 = st.checkbox("Enable Feature 1", value=False)
            flag2 = st.checkbox("Enable Feature 2", value=True)
            text_opt = st.text_input("Custom Selector (optional)", placeholder="main, article")
        with adv2:
            num_opt = st.number_input("Threshold", 0, 100, 50)
            select_opt = st.selectbox("Strategy", ["auto", "pruning", "bm25"])

    opts = {
        "mode": mode,
        "timeout": timeout,
        "cache_mode": cache_mode,
        "flag1": flag1,
        "flag2": flag2,
        "text_opt": text_opt or None,
        "num_opt": num_opt,
        "select_opt": select_opt,
    }

    return url, opts


# ============================================================
# RESULT VIEWER
# ============================================================

def render_results(results, output_dir, url):
    if not results:
        return

    st.divider()
    st.markdown("## 📊 Results")

    # Stats
    total = len(results)
    success = sum(1 for r in results if getattr(r, "success", False) or r.get("success", False))

    m1, m2, m3 = st.columns(3)
    m1.metric("Total", total)
    m2.metric("Succeeded", success)
    m3.metric("Failed", total - success)

    # Page selector
    st.markdown("### Result Viewer")
    page_options = []
    for i, r in enumerate(results):
        title = r.get("title", r.get("url", f"Result {i+1}")) if isinstance(r, dict) else getattr(r, "title", f"Result {i+1}")
        status = "✅" if (r.get("success") if isinstance(r, dict) else getattr(r, "success", False)) else "❌"
        page_options.append(f"{status} {i+1}. {str(title)[:60]}")

    selected = st.selectbox("Select Result", range(len(page_options)),
                             format_func=lambda x: page_options[x])
    result = results[selected]

    # Helper to get field from dict or object
    def get(r, key, default=""):
        if isinstance(r, dict):
            return r.get(key, default)
        return getattr(r, key, default)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📝 Output", "ℹ️ Metadata", "💾 Download"])

    with tab1:
        content = get(result, "content", "")
        if content:
            st.markdown(str(content))
        else:
            st.warning("No content available")

    with tab2:
        st.json({
            "url": get(result, "url"),
            "title": get(result, "title"),
            "success": get(result, "success"),
        })

    with tab3:
        content_str = str(get(result, "content", ""))
        if content_str:
            st.download_button(
                "📥 Download This Result",
                data=content_str.encode("utf-8"),
                file_name=f"result_{selected}.md",
                mime="text/markdown",
            )

        # Save all
        if st.button("💾 Save All to Files"):
            saved = 0
            for i, r in enumerate(results):
                c = get(r, "content", "")
                if c:
                    with open(os.path.join(output_dir, f"result_{i}.md"), "w") as f:
                        f.write(str(c))
                    saved += 1
            st.success(f"Saved {saved} files to `{output_dir}`")

        # ZIP download
        all_content = "\n\n---\n\n".join(
            str(get(r, "content", "")) for r in results if get(r, "content", "")
        )
        if all_content:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, r in enumerate(results):
                    c = get(r, "content", "")
                    if c:
                        zf.writestr(f"result_{i}.md", str(c))
            buf.seek(0)
            st.download_button(
                "📦 Download All as ZIP",
                data=buf.getvalue(),
                file_name="results.zip",
                mime="application/zip",
            )


# ============================================================
# EXECUTION
# ============================================================

def execute(url, opts, engine, output_dir):
    if not url:
        st.error("Please enter a URL")
        return

    if not url.startswith("http"):
        url = "https://" + url

    progress = st.progress(0, "Starting...")
    status_text = st.empty()

    def update_progress(done, total, current):
        progress.progress(min(done / total, 1.0))
        status_text.text(f"Processing {done}/{total}: {str(current)[:80]}")

    try:
        results = asyncio.run(run_tool(url, opts, update_progress))
        progress.progress(1.0)
        status_text.text(f"Done — {len(results)} results")

        st.session_state.current_results = results
        st.session_state.last_config = {"url": url, "opts": opts}
        st.session_state.history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "url": url,
            "count": len(results),
        })
    except Exception as e:
        st.error(f"Failed: {e}")
        st.exception(e)


# ============================================================
# MAIN
# ============================================================

def main():
    st.title("🔧 Tool Name Web App")
    st.caption("Description of what this tool does")

    engine, output_dir = render_sidebar()
    url, opts = render_config()

    st.divider()

    if st.button("🚀 Start", type="primary"):
        execute(url, opts, engine, output_dir)

    if st.session_state.current_results:
        render_results(st.session_state.current_results, output_dir,
                       st.session_state.last_config.get("url", url))


if __name__ == "__main__":
    main()