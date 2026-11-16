"""Streamlit UI: streamlit run app.py"""

import sys

sys.path.insert(0, "src")

import streamlit as st  # noqa: E402

from policy_agent import PolicyAgent  # noqa: E402

st.title("Policy Finder Agent")
folder = st.sidebar.text_input("Policy folder", "data/sample_policies")
agent = PolicyAgent(folder)

st.sidebar.subheader("Latest approved policies")
for d in agent.latest_policies():
    st.sidebar.write(f"**{d.policy_name}** v{d.version} ({d.effective_date})")

q = st.text_input("Ask about a company policy")
if q:
    ans = agent.ask(q)
    st.write(ans.text)
    for s in ans.sources:
        st.caption(f"Source: {s}")
