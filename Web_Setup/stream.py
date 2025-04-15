import streamlit as st
from PIL import Image

band_names = {"Goose": "Goose", "Phish": "Phish", "UM":"Umphrey's McGee", "WSP":"Widespread Panic"}
band_notebooks = {"Goose": "Rick's", "Phish": "Trey's", "UM":"Joel's", "WSP":"JoJo's"}

# --- CONFIGS ---
st.set_page_config(
	page_title="Jam Band Nerd Demo",
	page_icon="emoji"

st.title("Jam Band Nerd")
st.image("https://hevria.com/wp-content/uploads/2015/07/GD-rainbow2-1024x770.jpg")

# --- LOAD DATA ---
@st.cache_data
def load_data(band):
	data_notebook = pd.read_csv(notebook_{band)}
	data_notebook = pd.read_csv(notebook_{band)}
	return 
for band in bands:
	ckplus_{band}, notebook_{band} = load_data(band)

# ---- NAVIGATION MENU ---
selected = option_menu(
	menu_title = None,
	options = bands,
	#icons = [], https://icons.getboostrap.com/
	orientation="horizontal",
)

# --- TABS AND TABLES ---
if selected == "WSP":
	st.header("Widespread Panic")
	tab_1, tab_2 = st.tabs(2)
	with tab_1:
		st.header("CK+")
		st.dataframe(notebbook_{WSP})
	with tab_2:
		st.header("{band_notebooks}")
		st.dataframe(ckplus_{band})
if selected == "UM":
	st.header("Umphrey's McGee")
	tab_1, tab_2 = st.tabs(2)
	with tab_1:
		st.header("CK+")
		st.dataframe(notebbook_{UM})
	with tab_2:
		st.header("{band_notebooks}")
		st.dataframe(ckplus_{band})
if selected == "Phish":
	st.header("Phish")
	tab_1, tab_2 = st.tabs(2)
	with tab_1:
		st.header("CK+")
		st.dataframe(notebbook_{PHISH})
	with tab_2:
		st.header("{band_notebooks}")
		st.dataframe(ckplus_{band})
if selected == "Goose":
	st.header("Goose")
	tab_1, tab_2 = st.tabs(2)
	with tab_1:
		st.header("CK+")
		st.dataframe(notebbook_{GOOSE})
	with tab_2:
		st.header("{band_notebooks}")
		st.dataframe(ckplus_{band})


		
 