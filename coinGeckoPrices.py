import requests
import json
import streamlit as st

@st.cache
def coinGeckoPriceData(token_id):
  response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=usd")
  data = json.loads(response.text)
  return((data[f'{token_id}']['usd']))

