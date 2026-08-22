import streamlit as st
from transformers import pipeline

st.set_page_config(page_title="AI Sentiment Analyzer", page_icon="🤖", layout="centered")

@st.cache_resource
def load_pipeline():
    # Fast, pre-trained transformer model for sentiment analysis
    return pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

classifier = load_pipeline()

st.title("🤖 Real-Time Sentiment & Emotion Analyzer")
st.markdown("Enter any text, review, or feedback to analyze sentiment using a pre-trained Transformer model.")

user_text = st.text_area("Your Input:", placeholder="e.g., The product quality is amazing, really exceeded my expectations!")

if st.button("Analyze Sentiment", type="primary"):
    if user_text.strip():
        with st.spinner("Analyzing text..."):
            result = classifier(user_text)[0]
            label = result['label']
            score = result['score'] * 100

            st.divider()
            if label == "POSITIVE":
                st.success(f"### Sentiment: **Positive** 😊")
            else:
                st.error(f"### Sentiment: **Negative** 😞")
                
            st.progress(int(score))
            st.write(f"**Confidence Score:** `{score:.2f}%`")
    else:
        st.warning("Please enter some text before analyzing.")