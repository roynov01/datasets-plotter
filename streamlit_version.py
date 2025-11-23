import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------- Page/App title & credit --------------------
st.set_page_config(page_title="Roy plotter", layout="wide", page_icon="icon.ico")
st.markdown("<h1 style='text-align:center; margin-top:0;'>Roy plotter</h1>", unsafe_allow_html=True)
st.markdown("""
<style>
.roy-credit {
  position: fixed; right: 12px; bottom: 8px;
  color: #888888; font-size: 12px; z-index: 9999;
}
</style>
<div class="roy-credit">Made by Roy Novoselsky</div>
""", unsafe_allow_html=True)

# -------------------- Config & helpers --------------------
DATASETS_DIR = Path("datasets")
MANIFEST_PATH = DATASETS_DIR / "manifest.csv"

@st.cache_data
def load_manifest(path: Path) -> pd.DataFrame:
    mf = pd.read_csv(path)
    needed = {"file", "organism", "organ", "dataset_name", "paper_url"}
    missing = needed - set(mf.columns)
    if missing:
        raise ValueError(f"manifest.csv missing columns: {missing}")
    for col in ["file", "organism", "organ", "dataset_name", "paper_url"]:
        mf[col] = mf[col].astype(str)
    return mf

@st.cache_data
def load_dataset_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "gene" not in df.columns:
        raise ValueError(f"{path.name} must have a 'gene' column.")
    df["gene"] = df["gene"].astype(str)
    return df

def filter_manifest(mf: pd.DataFrame, organism: str | None = None, organ: str | None = None) -> pd.DataFrame:
    out = mf
    if organism:
        out = out[out["organism"] == organism]
    if organ:
        out = out[out["organ"] == organ]
    return out

def build_expr_df(row: pd.Series) -> pd.DataFrame:
    out = row.drop(labels="gene").reset_index()
    out.columns = ["celltype", "expression"]
    return out

def find_gene_row(df: pd.DataFrame, gene: str):
    if not gene:
        return None
    m = df[df["gene"].str.upper() == gene.upper()]
    return None if m.empty else m.iloc[0]

def _trigger_compute():
    st.session_state["trigger_compute"] = True
    
# -------------------- Load manifest --------------------
try:
    manifest = load_manifest(MANIFEST_PATH)
except Exception as e:
    st.error(f"Could not load manifest at {MANIFEST_PATH}:\n{e}")
    st.stop()

# -------------------- Dropdowns row: organism → organ → dataset --------------------
c1, c2, c3 = st.columns(3)
with c1:
    organisms = sorted(manifest["organism"].unique().tolist())
    sel_organism = st.selectbox("Organism", organisms, index=0 if organisms else None)
with c2:
    mf_o = filter_manifest(manifest, organism=sel_organism)
    organs = sorted(mf_o["organ"].unique().tolist())
    sel_organ = st.selectbox("Organ", organs, index=0 if organs else None)
with c3:
    mf_oo = filter_manifest(manifest, organism=sel_organism, organ=sel_organ)
    ds_options = mf_oo["dataset_name"].tolist()
    default_idx = 0
    if "dataset_name" in st.session_state and st.session_state["dataset_name"] in ds_options:
        default_idx = ds_options.index(st.session_state["dataset_name"])
    sel_dataset_name = st.selectbox("Dataset", ds_options, index=default_idx if ds_options else None)

# Resolve selected dataset row
selected_row = mf_oo[mf_oo["dataset_name"] == sel_dataset_name].iloc[0] if not mf_oo.empty else None
paper_url = selected_row["paper_url"] if selected_row is not None else None
ds_path = DATASETS_DIR / selected_row["file"] if selected_row is not None else None

# -------------------- Gene entry + button --------------------
if "current_gene_input" not in st.session_state:
    st.session_state["current_gene_input"] = "GAPDH"
st.markdown("**Enter a gene name**")

c_gene, c_btn, c_spacer = st.columns([2.2, 0.5, 0.3])
with c_gene:
    gene_input = st.text_input(
        "Gene",
        label_visibility="collapsed",
        placeholder="e.g., GAPDH",
        key="current_gene_input",
        on_change=_trigger_compute
    )
with c_btn:
    submitted = st.button("Show")
    submitted = submitted or st.session_state.pop("trigger_compute", False)



# -------------------- Load current dataset --------------------
current_df = None
if ds_path is not None:
    try:
        current_df = load_dataset_csv(ds_path)
    except Exception as e:
        st.error(f"Failed to load dataset '{sel_dataset_name}' ({ds_path.name}): {e}")
        st.stop()


dataset_changed = sel_dataset_name != st.session_state.get("dataset_name")
if dataset_changed:
    st.session_state["dataset_name"] = sel_dataset_name  # remember last dataset

# 1) If user submitted, use their input
if submitted and current_df is not None:
    g = (st.session_state.get("current_gene_input") or "").strip()
    row = find_gene_row(current_df, g)
    if row is None:
        st.session_state["bar_expr_df"] = None
        st.session_state["bar_warning"] = f"No data for gene: {g}"
    else:
        st.session_state["bar_expr_df"] = build_expr_df(row)
        st.session_state["bar_warning"] = None

# 2) Else if dataset changed, recompute using the SAME gene (if any)
elif dataset_changed and current_df is not None:
    g = (st.session_state.get("current_gene_input") or "").strip()
    row = find_gene_row(current_df, g) if g else None
    if row is None:
        st.session_state["bar_expr_df"] = None
        st.session_state["bar_warning"] = f"'{g}' not found in {sel_dataset_name}." if g else None
    else:
        st.session_state["bar_expr_df"] = build_expr_df(row)
        st.session_state["bar_warning"] = None

# 3) Else first-load default
elif current_df is not None and st.session_state.get("bar_expr_df") is None and st.session_state.get("bar_warning") is None:
    init_gene = (st.session_state.get("current_gene_input") or "GAPDH").strip()
    row = find_gene_row(current_df, init_gene)
    if row is None and not current_df.empty:
        row = current_df.iloc[0]
    if row is not None:
        st.session_state["bar_expr_df"] = build_expr_df(row)
    else:
        st.session_state["bar_warning"] = "No data available in this dataset."


# -------------------- Barplot --------------------
if st.session_state.get("bar_warning"):
    st.warning(st.session_state["bar_warning"])
elif st.session_state.get("bar_expr_df") is not None:
    gene_title = (st.session_state.get("current_gene_input") or "").upper()
    fig_bar = px.bar(st.session_state["bar_expr_df"], x="celltype", y="expression")
    fig_bar.update_layout(
        title=dict(text=gene_title, x=0.5, xanchor="center"),
        font=dict(color="black"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    fig_bar.update_xaxes(title_text=None, tickfont=dict(color="black"))
    fig_bar.update_yaxes(
        title=dict(text="Expression", font=dict(color="black")),
        tickfont=dict(color="black")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    if paper_url and isinstance(paper_url, str) and paper_url.strip():
        st.markdown(f"[Reference for **{sel_dataset_name}**]({paper_url})")
else:
    st.info("Choose organism, organ, dataset, enter a gene, and press **Show** (or hit Enter).")
