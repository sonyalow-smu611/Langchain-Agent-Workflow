import streamlit as st


st.set_page_config(page_title="Study Planning Agent", page_icon=":books:")
st.title("Study Planning Agent")
st.caption("Create a cheatsheet and content/practice study plan from course_notes.txt.")


@st.cache_resource
def get_agent_executor():
    """Create the LangChain agent once and reuse it across Streamlit reruns."""
    from study_planner import build_agent

    return build_agent()


if "chat_history" not in st.session_state:
    # Store simple display messages; convert them to LangChain messages on invoke.
    st.session_state.chat_history = []

if st.sidebar.button("Clear chat"):
    st.session_state.chat_history = []
    st.rerun()

st.sidebar.markdown("### Try")
st.sidebar.markdown("- I want to study transformers and attention.")
st.sidebar.markdown("- Make it 3 study sessions.")
st.sidebar.markdown("- Give me more practice on tokens and embeddings.")

if not st.session_state.chat_history:
    with st.chat_message("assistant"):
        st.markdown(
            "Ask me what topic you want to study. I will search the notes, "
            "create one cheatsheet, create a study plan, and save it to `study_plan.txt`."
        )

for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

user_query = st.chat_input("What topic do you want to study?")

if user_query:
    previous_history = st.session_state.chat_history.copy()

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Planning from course notes..."):
            try:
                from langchain_core.messages import AIMessage, HumanMessage

                agent_history = [
                    HumanMessage(content=message["content"])
                    if message["role"] == "user"
                    else AIMessage(content=message["content"])
                    for message in previous_history
                ]
                result = get_agent_executor().invoke(
                    {"input": user_query, "chat_history": agent_history}
                )
                response = result["output"]
                st.markdown(response)
            except Exception as error:
                response = f"Agent failed: {error}"
                st.error(response)

    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({"role": "assistant", "content": response})
