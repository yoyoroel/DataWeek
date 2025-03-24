import streamlit as st

# --- CSS voor een bovenste navigatiebalk ---
st.markdown(
    """
    <style>
    .topnav {
        background-color: #333;
        overflow: hidden;
        width: 100%;
        display: flex;
        justify-content: center;
        padding: 10px 0;
        position: fixed;
        top: 2cm;
        left: 0;
        z-index: 1000;
    }
    .topnav a {
        color: white;
        padding: 14px 20px;
        text-decoration: none;
        font-size: 17px;
    }
    .topnav a:hover {
        background-color: #ddd;
        color: black;
    }
    body {
        padding-top: 60px; /* Zorgt ervoor dat de inhoud niet overlapt met de navigatiebalk */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Pagina State ---
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# --- Functie om pagina te wisselen ---
def switch_page(page_name):
    st.session_state["page"] = page_name

# --- HTML Navigatiebalk ---
st.markdown(
    """
    <div class="topnav">
        <a href="#" onclick="set_page('Home')">Home</a>
        <a href="#" onclick="set_page('Over')">Over</a>
        <a href="#" onclick="set_page('Contact')">Contact</a>
    </div>
    
    <script>
    function set_page(page) {
        var data = {"page": page};
        fetch('/_stcore/script_run', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).then(response => {
            window.location.reload();
        });
    }
    </script>
    """,
    unsafe_allow_html=True,
)

# --- Inhoud van de pagina’s ---
if st.session_state["page"] == "Home":
    st.title("🏠 Homepagina")
    st.write("Welkom op de homepagina!")
elif st.session_state["page"] == "Over":
    st.title("ℹ️ Over Ons")
    st.write("Dit is de over ons pagina.")
elif st.session_state["page"] == "Contact":
    st.title("📞 Contact")
    st.write("Neem contact met ons op.")