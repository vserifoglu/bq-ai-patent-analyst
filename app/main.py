import streamlit as st

from components.header import render_header
from core.app_controller import AppController
from core.dashboard import DashboardEngine
from core.state_manager import StreamlitStateManager

import streamlit as st
import json

# --- TEMPORARY DEBUG BLOCK ---
# This will help us see exactly what the app is receiving.
st.subheader("🕵️‍♂️ Debug Information")
with st.expander("Click here to see secret details"):
    # 1. Check if the secret exists
    if "GCP_SA_KEY" in st.secrets:
        st.success("GCP_SA_KEY secret found!")

        key_string = st.secrets["GCP_SA_KEY"]

        # 2. Check the type and length of the secret
        st.write(f"Type of secret: {type(key_string)}")
        st.write(f"Length of secret string: {len(key_string)}")

        # 3. Try to parse it as JSON and see the specific error
        try:
            key_dict = json.loads(key_string)
            st.success("Successfully parsed secret as JSON.")
            # Print a safe part of the key to confirm it's correct
            st.write(f"Project ID from key: {key_dict.get('project_id', 'Not found')}")
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse secret as JSON. This is the root cause.")
            st.write(f"JSONDecodeError: {e}")
            st.code(key_string, language="text") # Display the malformed string
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

    else:
        st.error("GCP_SA_KEY secret NOT found in Streamlit secrets!")
# --- END OF DEBUG BLOCK ---

def main():
    """Main application entry point"""
    # Initialize components with configuration
    controller = AppController()  # Uses config from environment
    state_manager = StreamlitStateManager()
    engine = DashboardEngine(controller, state_manager)
    
    # Render app header
    render_header()
    
    # Page title
    st.markdown("# 🔬 AI Patent Analyst")
    st.markdown("*From Unstructured PDFs to Queryable Knowledge Graph*")
    
    # Two-tab layout (Visualization first)
    tab1, tab2 = st.tabs(["📊 Data Analysis", "🔎 Semantic Search"])

    with tab1:
        # Engine handles data analysis tab first
        engine.run_data_tab()

    with tab2:
        # Engine orchestrates home & search as second tab
        engine.run()


if __name__ == "__main__":
    main()
