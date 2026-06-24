---
name: streamlit-tool-ui
description: "Build a Streamlit web app that wraps a Python tool or library with a configurable, user-friendly UI. Covers the full pattern: sidebar config panels, tabbed result viewers, progress bars for async work, download/export features, and graceful degradation when optional dependencies are missing. Use when the user wants to 'create a web app', 'build a UI for X tool', 'make a Streamlit app', 'wrap CLI in web interface', or 'add a frontend to a Python script'."
version: 1.0.0
tags:
  - streamlit
  - web-app
  - ui
  - python
  - frontend
  - tool-wrapper
  - dashboard
---

# Streamlit Tool UI

Wrap a Python tool, CLI, or library in a Streamlit web app with a full configuration
UI, result viewer, and export features. This is a recurring pattern: the user wants
to make a tool accessible to non-technical users or to have a visual interface for
customizing parameters that would otherwise be command-line flags.

## When to Use

- User asks to "create a web app" or "build a UI" for a Python tool/library
- User wants to make a CLI tool accessible via browser
- User wants visual configuration of parameters (dropdowns, sliders, toggles)
- User needs a result viewer with tabs for different output formats
- User wants to wrap an async Python library (httpx, crawl4ai, etc.) in a UI

## Architecture Pattern

Every tool-wrapper Streamlit app follows this structure:

```
1. Page config (title, icon, layout)
2. Session state init (history, results, current selection)
3. Dependency detection (auto-detect optional packages, fall back gracefully)
4. Sidebar: engine/mode selection + global options
5. Main area: tool-specific config form (URLs, parameters, filters)
6. Execute button → run async work → show progress
7. Result viewer: tabs (output, raw data, metadata) + download/export
```

## App Structure Template

```python
#!/usr/bin/env python3
import streamlit as st
import asyncio

st.set_page_config(page_title="Tool Name", page_icon="🔧", layout="wide")

# --- Session state ---
if "results" not in st.session_state:
    st.session_state.results = None
if "history" not in st.session_state:
    st.session_state.history = []

# --- Dependency detection ---
@st.cache_data
def check_dependency():
    try:
        import some_optional_lib
        return True
    except ImportError:
        return False

DEPS_AVAILABLE = check_dependency()

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🔧 Tool Name")
    st.caption("Short description")
    engine = st.radio("Engine", ["Full Mode", "Fallback Mode"]) if DEPS_AVAILABLE else "Fallback Mode"
    if not DEPS_AVAILABLE:
        st.warning("Optional dependency not available. Using fallback.")
    output_dir = st.text_input("Output Directory", value="/workspace/output")

# --- Config form ---
st.markdown("### ⚙️ Configuration")
col1, col2 = st.columns(2)
with col1:
    url = st.text_input("URL", placeholder="https://...")
    primary_option = st.selectbox("Mode", ["option_a", "option_b"])
with col2:
    timeout = st.number_input("Timeout (ms)", 5000, 120000, 30000)
    cache_mode = st.selectbox("Cache", ["A", "B", "C"])

# Advanced options in expander
with st.expander("🔧 Advanced Options"):
    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        flag1 = st.checkbox("Option 1", value=False)
        flag2 = st.checkbox("Option 2", value=True)
    with adv_col2:
        text_opt = st.text_input("Custom selector", placeholder="optional")

# --- Build options dict ---
opts = {
    "url": url,
    "mode": primary_option,
    "timeout": timeout,
    "cache": cache_mode,
    "flag1": flag1,
    "flag2": flag2,
    "selector": text_opt or None,
}

# --- Execute ---
if st.button("🚀 Run", type="primary"):
    with st.spinner("Working..."):
        results = asyncio.run(run_tool(url, opts))
        st.session_state.results = results

# --- Results ---
if st.session_state.results:
    render_results(st.session_state.results)
```

## Key Patterns

### 1. Dependency Detection with Graceful Fallback

Always detect optional dependencies and offer a fallback mode. Never hard-fail.

```python
@st.cache_data
def check_tool_available():
    try:
        import expensive_lib
        # Actually try to use it, not just import
        result = expensive_lib.test()
        return True, "OK"
    except Exception as e:
        return False, str(e)

AVAILABLE, MSG = check_tool_available()
```

In the sidebar:
- If available: radio button to let user choose engine
- If not available: show warning + auto-select fallback

### 2. Async Execution

Streamlit is synchronous. Wrap async code with `asyncio.run()`:

```python
if st.button("Run"):
    results = asyncio.run(my_async_function(url, opts))
```

For long-running async with progress:

```python
progress = st.progress(0, "Starting...")
status = st.empty()

def update(done, total, current):
    progress.progress(done / total)
    status.text(f"Processing {done}/{total}: {current}")

results = asyncio.run(crawl_with_progress(url, opts, update_callback=update))
```

### 3. Config Form Layout

- Use `st.columns(2)` for paired options (URL + format, timeout + cache)
- Group advanced/rarely-used options in `st.expander("🔧 Advanced Options")`
- Group related filter options in nested expanders
- Every checkbox/selectbox should have a `help=` tooltip
- Use emoji prefixes for section headers (⚙️ 🔧 📊 💾 📝)

### 4. Result Viewer with Tabs

```python
tab1, tab2, tab3, tab4 = st.tabs(["📝 Output", "🌐 Raw", "🔗 Links", "ℹ️ Info"])

with tab1:
    st.markdown(result.markdown)

with tab2:
    st.code(result.html[:50000], language="html")

with tab3:
    # Lists, tables, links
    for item in result.links:
        st.markdown(f"- [{item['text']}]({item['url']})")

with tab4:
    st.json({
        "url": result.url,
        "status": result.status_code,
        "success": result.success,
    })
```

### 5. Download & Export

Three export patterns:

```python
# Single file download
st.download_button("📥 Download", data=content.encode(), file_name="output.md")

# Save all to disk
if st.button("💾 Save All"):
    save_results_to_files(results, output_dir)

# ZIP download (for multi-file output)
import zipfile, io
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
    for r in results:
        zf.writestr(filename, content)
buf.seek(0)
st.download_button("📦 Download ZIP", data=buf.getvalue(), file_name="results.zip")
```

### 6. Stats Dashboard

After results are ready, show summary metrics:

```python
col1, col2, col3 = st.columns(3)
col1.metric("Total", len(results))
col2.metric("Success", sum(1 for r in results if r.success))
col3.metric("Failed", len(results) - successes)
```

### 7. Session State for History

```python
if "history" not in st.session_state:
    st.session_state.history = []

# After each run
st.session_state.history.append({
    "time": datetime.now().strftime("%H:%M:%S"),
    "url": url,
    "pages": len(results),
})

# In sidebar
for entry in reversed(st.session_state.history[-5:]):
    st.caption(f"{entry['time']} — {entry['pages']} pages")
```

## Running the App

```bash
# Streamlit needs to be on PATH or use full path
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true

# If streamlit is not on PATH:
~/.local/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

**Pitfall:** On shared servers, `streamlit` may not be on PATH even after `pip install`.
Check `pip show streamlit` for the `Location`, then find the binary at
`<location>/../../../bin/streamlit` or use `python3 -m streamlit run app.py`.

## Common Pitfalls

1. **streamlit not on PATH**: After `pip install streamlit` on a non-root user,
   the binary is at `~/.local/bin/streamlit`. Use the full path or `python3 -m streamlit`.

2. **asyncio.run() in Streamlit**: Streamlit reruns the script on each interaction.
   `asyncio.run()` creates a new event loop each time, which is fine for one-shot
   execution. For long-running background tasks, use `st.session_state` to persist
   async objects across reruns (advanced pattern).

3. **Progress bars with async**: Use `st.progress()` + callback pattern. The callback
   is called from within the async function via `asyncio.run()`. Since Streamlit
   reruns are synchronous, the progress bar updates work correctly within a single
   `asyncio.run()` call.

4. **Large outputs in st.code()**: Truncate to ~50,000 chars to avoid browser lag:
   `st.code(content[:50000], language="markdown")`.

5. **ZIP in memory**: Use `io.BytesIO()` + `zipfile.ZipFile` to create downloadable
   ZIPs without writing to disk. Always `.seek(0)` before passing to `st.download_button`.

6. **Session state keys**: Initialize all session state keys at the top of the script
   before any conditional blocks. Streamlit reruns the entire script on each interaction.

## Testing the App

```bash
# Check health
curl -s http://localhost:8501/_stcore/health
# Should return "ok"

# Check page loads
curl -sI http://localhost:8501/
# Should return 200

# Verify no import errors in logs
```

## File Delivery to User

When the user needs files from the app, provide them via `MEDIA:` prefix in chat
responses. For multi-file output, create a ZIP archive:

```python
import shutil
shutil.make_archive('/path/to/output', 'zip', '.', 'output_dir')
```

Then reference as `MEDIA:/path/to/output.zip` in the chat response.

## Support Files

- `templates/tool_ui_template.py` — Full Streamlit app template with sidebar config,
  async execution, progress bars, tabbed results, and ZIP export. Copy and customize
  for any Python tool.