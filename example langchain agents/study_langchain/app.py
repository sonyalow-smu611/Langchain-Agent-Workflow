# run `streamlit run app.py`

import os

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

import study_resource_generator as app


st.set_page_config(page_title="Study Resource Generator", page_icon=":books:")
st.title("Study Resource Generator")
st.caption("Turn the .txt notes in documents/ into a cheatsheet, summary, notes, or quiz.")

RESOURCES = {
    "Cheatsheet": "cheatsheet",
    "1 page summary": "summary",
    "In depth organised notes": "notes",
    "Quiz": "quiz",
}


@st.cache_resource
def get_study_tools():
    """Build the retriever and the four chains once and reuse them across reruns."""
    documents = app.load_study_documents()
    if not documents:
        return None, None

    return app.create_retriever(documents), app.create_study_agents()


if not os.getenv("OPENAI_API_KEY"):
    st.error(
        f"OPENAI_API_KEY is not set. Add it to `{app.ENV_PATH}` "
        "(copy `.env.example` to get started), then reload this page."
    )
    st.stop()

if "chat_history" not in st.session_state:
    # Store simple display messages; convert them to LangChain messages on invoke.
    # Turns where no notes matched are shown but not sent back to the model.
    st.session_state.chat_history = []

resource_label = st.sidebar.radio("Study resource", list(RESOURCES))

if st.sidebar.button("Clear chat"):
    st.session_state.chat_history = []
    st.rerun()

if st.sidebar.button("Reload notes"):
    # The vector store is cached, so rebuild it after adding or editing files.
    get_study_tools.clear()
    st.rerun()

st.sidebar.markdown("### Try")
st.sidebar.markdown("- Calvin cycle")
st.sidebar.markdown("- Limiting factors of photosynthesis")
st.sidebar.markdown("- Light-dependent reactions")

with st.spinner("Loading study resources and creating vector store..."):
    retriever, study_agents = get_study_tools()

if retriever is None:
    st.warning(
        f"No .txt study resources found in `{app.documents_dir}`. "
        "Add your notes to that folder, then click **Reload notes**."
    )
    st.stop()

if not st.session_state.chat_history:
    with st.chat_message("assistant"):
        st.markdown(
            "Pick a study resource in the sidebar, then tell me the topic, chapter, "
            "or question to focus on. I only use the notes in `documents/`."
        )

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

focus = st.chat_input("Enter the topic, chapter, or question to focus on")

if focus:
    agent_name = RESOURCES[resource_label]
    request_label = f"**{resource_label}:** {focus}"
    previous_history = st.session_state.chat_history.copy()

    with st.chat_message("user"):
        st.markdown(request_label)

    with st.chat_message("assistant"):
        with st.spinner(f"Writing your {resource_label.lower()}..."):
            generated = False
            try:
                context = app.retrieve_context(retriever, focus)

                if context == app.NO_CONTEXT:
                    # Same rule as the CLI: without matching notes, skip the model.
                    response = (
                        f"No notes in `documents/` matched '{focus}'. "
                        "Try a different topic, or add notes that cover it."
                    )
                    st.warning(response)
                else:
                    agent_history = [
                        SystemMessage(
                            content="You are a helpful study assistant that only uses the uploaded study resources."
                        )
                    ] + [
                        HumanMessage(content=message["request"])
                        if message["role"] == "user"
                        else AIMessage(content=message["content"])
                        for message in previous_history
                        if message["generated"]
                    ] + [HumanMessage(content=f"Generate {agent_name} for: {focus}")]

                    response = study_agents[agent_name].invoke(
                        {
                            "chat_history": app.format_chat_history(agent_history),
                            "context": context,
                            "focus": focus,
                        }
                    )
                    st.markdown(response)
                    generated = True
            except Exception as error:
                response = f"Agent failed: {error}"
                st.error(response)

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": request_label,
            "request": f"Generate {agent_name} for: {focus}",
            "generated": generated,
        }
    )
    st.session_state.chat_history.append(
        {"role": "assistant", "content": response, "generated": generated}
    )
