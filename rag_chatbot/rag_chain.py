import streamlit as st
import hashlib
import json
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from rag_chatbot.data_loader import load_json_documents
import os

#  Path to your invoice data
json_path =  json_path = os.path.abspath("data/all_invoices_data.json")


#  Hashing function to detect JSON changes
def get_json_hash(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

#  Cached vectorstore setup (uses hash to detect changes)
@st.cache_resource(show_spinner=True)
def setup_vectorstore(json_hash: str):  # use hash as a cache key
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    docs = load_json_documents(json_path)
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory = os.path.abspath("D:\Documents\Document _Extraction\Project\database\vector_db")
    )
    return vectorstore.as_retriever(search_kwargs={"k": 2})

# Main RAG Chatbot App
def run_chatbot():
    st.markdown("<h3 style='color:#FF0000;'>Chat with Invoice AI </h3>", unsafe_allow_html=True)

    # Initialize LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

    # Memory for chat history
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

    # Get hash of current JSON
    json_hash = get_json_hash(json_path)

    # Rebuild vectorstore only if file content changed
    if "last_json_hash" not in st.session_state or json_hash != st.session_state.last_json_hash:
        
        st.session_state.retriever = setup_vectorstore(json_hash)
        st.session_state.last_json_hash = json_hash

    # Build RAG chain
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=st.session_state.retriever,
        memory=st.session_state.memory
    )


    # Display chat history
    for msg in st.session_state.memory.chat_memory.messages:
        if msg.type == "human":
            st.chat_message("user").write(msg.content)
        elif msg.type == "ai":
            st.chat_message("assistant").write(msg.content)

    # Chat input
    user_input = st.chat_input("Ask something about the invoice data...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        with st.spinner("🤖 Thinking..."):
            response = rag_chain.run(user_input)
        with st.chat_message("assistant"):
            st.write(response)

    # Debug / Utility buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧠 Show Memory"):
            st.subheader("Chat History")
            for msg in st.session_state.memory.chat_memory.messages:
                st.markdown(f"**{msg.type.capitalize()}:** {msg.content}")
    with col2:
        if st.button("🗑️ Clear Memory"):
            st.session_state.memory.clear()
            st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            st.success("Memory cleared!")

    # Footer
    st.markdown("""
        <div style="text-align:center; color:#888; margin-top:2em;">
            Created by <strong style="color:#FF0000;">Krishnan</strong> 🚀 | Powered by LangChain + Gemini
        </div>
    """, unsafe_allow_html=True)


