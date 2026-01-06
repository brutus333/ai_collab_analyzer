import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="IA Collaboration Insights Platform", layout="wide")

API_URL = "http://localhost:8000"

st.title("🧠 Human-AI Collaboration Insights Platform")
st.markdown("---")

# Sidebar - Repo Selection & Mode
st.sidebar.header("Navigation")

# Global State
try:
    repos_resp = requests.get(f"{API_URL}/repositories")
    if repos_resp.status_code == 200:
        repos = repos_resp.json()
    else:
        repos = []
except:
    repos = []

mode = st.sidebar.radio("View Mode", ["Portfolio Overview", "Repository Deep-Dive", "Industry Benchmarks", "Artifact Explorer"])

if mode == "Portfolio Overview":
    st.header("🏢 Portfolio Health & Performance")
    
    portfolio_resp = requests.get(f"{API_URL}/portfolio")
    if portfolio_resp.status_code == 200:
        p = portfolio_resp.json()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Repos", p['total_repos'])
        c2.metric("Avg Health", f"{p['avg_health_score']:.1f}")
        c3.metric("Avg Coherence", f"{p['avg_coherence_score']:.1f}")
        c4.metric("Avg Risk", f"{p['avg_risk_score']:.1f}", delta_color="inverse")
        
        st.markdown("---")
        
        col_chart, col_files = st.columns([2, 1])
        
        with col_chart:
            st.subheader("Cross-Repository Comparison")
            if p['repo_comparisons']:
                df_comp = pd.DataFrame(p['repo_comparisons'])
                fig = px.bar(df_comp, x='name', y=['health', 'coherence', 'risk'], 
                           barmode='group', title="Metric Comparison across Projects")
                st.plotly_chart(fig, use_container_width=True)
                
        with col_files:
            st.subheader("🔥 Top Portfolio Risks")
            if p['top_risky_files']:
                st.table(pd.DataFrame(p['top_risky_files']))
            else:
                st.write("No high-risk files detected.")
    else:
        st.warning("Could not fetch portfolio data. Ensure API is running.")

elif mode == "Repository Deep-Dive":
    if not repos:
        st.warning("No repositories found in database.")
    else:
        repo_names = [r['name'] for r in repos]
        selected_repo_name = st.sidebar.selectbox("Select Repository", repo_names)
        selected_repo = next(r for r in repos if r['name'] == selected_repo_name)
        
        st.header(f"🔍 Deep-Dive: {selected_repo['name']}")
        st.info(f"Path: {selected_repo['path']} | Last Analyzed: {selected_repo['last_analyzed']}")

        # Fetch Trends
        trends_resp = requests.get(f"{API_URL}/repositories/{selected_repo['name']}/trends")
        if trends_resp.status_code == 200:
            trends = trends_resp.json()
            if trends['dates']:
                df_trends = pd.DataFrame({
                    'Time': trends['dates'],
                    'Health': trends['health'],
                    'Coherence': trends['coherence'],
                    'Risk': trends['risk']
                })
                
                # Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Health", f"{trends['health'][-1]:.1f}")
                m2.metric("Coherence", f"{trends['coherence'][-1]:.1f}")
                m3.metric("Risk", f"{trends['risk'][-1]:.1f}", delta_color="inverse")
                
                st.subheader("Historical Evolution")
                fig = px.line(df_trends, x='Time', y=['Health', 'Coherence', 'Risk'],
                             title="Metric Trends Over Time")
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        # Latest Details
        results_resp = requests.get(f"{API_URL}/repositories/{selected_repo['name']}/results?limit=1")
        if results_resp.status_code == 200 and results_resp.json():
            latest = results_resp.json()[0]['data']
            d1, d2 = st.columns(2)
            with d1:
                st.write("**Recent Prompt Artifacts**")
                prompts = latest.get('prompts', [])
                if prompts:
                    st.dataframe(pd.DataFrame(prompts))
            with d2:
                st.write("**Code Hotspots**")
                hotspots = latest.get('hotspots', [])
                if hotspots:
                    df_h = pd.DataFrame(hotspots).rename(columns={'filepath': 'File', 'change_count': 'Commits'})
                    st.bar_chart(df_h[['File', 'Commits']].set_index('File'))

        st.markdown("---")
        st.subheader("💡 Actionable Insights")
        rec_resp = requests.get(f"{API_URL}/repositories/{selected_repo['name']}/recommendations")
        if rec_resp.status_code == 200:
            recs = rec_resp.json()
            if not recs:
                st.write("No urgent recommendations at this time. Great job!")
            else:
                for r in recs:
                    with st.expander(f"{r['severity'].upper()}: {r['title']}"):
                        st.write(f"**Description:** {r['description']}")
                        st.write(f"**Action:** {r['action_item']}")
                        st.write(f"**Rationale:** {r['rationale']}")
                        st.info(f"Affected Areas: {', '.join(r['affected_areas'])}")
        else:
            st.error("Could not fetch recommendations.")

elif mode == "Industry Benchmarks":
    if not repos:
        st.warning("No repositories found.")
    else:
        repo_names = [r['name'] for r in repos]
        selected_repo_name = st.sidebar.selectbox("Select Repository to Benchmark", repo_names)
        
        st.header(f"📊 Industry Benchmarking: {selected_repo_name}")
        
        bench_resp = requests.get(f"{API_URL}/repositories/{selected_repo_name}/benchmarks")
        if bench_resp.status_code == 200:
            benchmarks = bench_resp.json()
            
            for b in benchmarks:
                st.subheader(f"Metric: {b['metric_name'].replace('_', ' ').title()}")
                col_m, col_g = st.columns([1, 2])
                
                with col_m:
                    st.metric("Your Score", f"{b['repo_value']:.2f}")
                    st.write(f"**Industry Average:** {b['industry_avg']:.1f}")
                    st.write(f"**Percentile ranking:** {b['percentile']:.1f}%")
                    
                    if b['rating'] == 'Excellence': st.success("🌟 " + b['rating'])
                    elif b['rating'] in ['Strong', 'Standard']: st.info("✅ " + b['rating'])
                    else: st.warning("⚠️ " + b['rating'])
                
                with col_g:
                    # Simple gauge-like bar
                    st.progress(max(0, min(int(b['percentile']), 100)))
                st.markdown("---")
        else:
            st.error("Failed to fetch benchmarks.")

elif mode == "Artifact Explorer":
    st.header("🔍 Cross-Repository Artifact Explorer")
    st.markdown("Search through all historical commits, prompts, and file risks.")
    
    q = st.text_input("Search query (e.g. 'refactor', 'API', 'model')")
    cat = st.selectbox("Category", ["all", "prompt", "commit", "file"])
    
    if q:
        search_resp = requests.get(f"{API_URL}/search", params={"query": q, "category": cat})
        if search_resp.status_code == 200:
            results = search_resp.json()
            if results:
                st.write(f"Found {len(results)} results:")
                df_res = pd.DataFrame(results)
                st.table(df_res)
            else:
                st.info("No matching artifacts found.")
        else:
            st.error("Search failed.")
