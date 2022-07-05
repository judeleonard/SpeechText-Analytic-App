mkdir -p ~/.streamlit/
echo "[theme]
base='dark'
primaryColor='#d33682'
backgroundColor='#002b36'
secondaryBackgroundColor='#558866'
textColor='fafafa'
font = 'sans serif'
[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
