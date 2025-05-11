import os
import streamlit as st
import time
from dotenv import load_dotenv
import sys
import shutil

# Add the current directory to the path so that Python can find our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Decide which app to load based on environment or query parameter
def main():
    st.set_page_config(
        page_title="RAG Q-A System",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check for lightweight mode via query parameter
    query_params = st.experimental_get_query_params()
    lightweight_mode = query_params.get("lightweight", ["false"])[0].lower() == "true"
    
    # Header
    st.title("RAG Q-A System" + (" (Lightweight)" if lightweight_mode else ""))
    
    if not os.getenv("GOOGLE_API_KEY") and not lightweight_mode:
        st.warning("⚠️ No API key found. Running in lightweight mode.")
        lightweight_mode = True
    
    # Determine which app to run
    if lightweight_mode:
        st.info("🔍 Running in lightweight mode (document retrieval only, no LLM generation)")
        st.markdown("Switch to [Full Version](?lightweight=false) if you have an API key configured.")
        
        # Import and run the lightweight app
        from streamlit_app_light import main_app as light_app
        light_app()
    else:
        st.info("🧠 Running with full LLM capability")
        st.markdown("Switch to [Lightweight Version](?lightweight=true) if you hit API quota limits.")
        
        # Import and run the full app
        try:
            from streamlit_app import main_app as full_app
            full_app()
        except Exception as e:
            st.error(f"Error loading full app: {e}")
            st.warning("Falling back to lightweight mode due to error")
            from streamlit_app_light import main_app as light_app
            light_app()

if __name__ == "__main__":
    try:
        # Load environment variables
        load_dotenv(verbose=True)
        
        # For Streamlit Cloud: Try to get API key from secrets
        if not os.getenv("GOOGLE_API_KEY"):
            try:
                os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
            except:
                st.warning("No Google API key found in environment or secrets.")
        
        main()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please check the logs for more information.") 