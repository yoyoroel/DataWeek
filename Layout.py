import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import matplotlib.pyplot as plt
from PIL import Image


#data import en manipulatie
A350H = pd.read_excel('A350H.xlsx')
A321H = pd.read_excel('A321H.xlsx')

A350H['Hoogte (ft)'] = A350H['Hoogte (m)'] * 3.28084
A321H['Hoogte (ft)'] = A321H['Hoogte (m)'] * 3.28084

Jaar = pd.read_csv('GeluidsmetingGoed_2024.csv',index_col=0)

st.set_page_config(layout="wide")

# Banner met CSS
# Banner met CSS en afbeelding
st.markdown(
    """
    <style>
    .blue-banner {
        background-color: #0B1560;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .blue-banner h1 {
        color: white;
        margin: 0;
    }
    .blue-banner h3 {
        color: #cccccc;
        margin: 4px 0 0 0;
        font-weight: normal;
        font-size: 16px;
    </style>
    """,
    unsafe_allow_html=True
)

# Laad de afbeelding (zorg ervoor dat het pad klopt)
image = Image.open('Finnair Logo.png')  # Zorg ervoor dat dit pad correct is

# Plaats de banner met het logo
st.markdown('''
    <div class="blue-banner">
        <div>
            <h1>Titel</h1>
            <h3>Gemaakt door Gem, Roel en Mariah</h3>
        </div>
    </div>
'''.format(st.image(image, use_column_width=False, output_format="PNG")), unsafe_allow_html=True)

# Hoofdtabs
tabs = st.tabs(["Home", "Finnair", "Geluid"])

# Tab 1
with tabs[0]:
    st.header("Home")
    st.write("Welkom op de homepage!")

# Tab 2
with tabs[1]:
    st.header("Finnair")

    # Maak 2 kolommen: linker fake-sidebar en rechter content
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("### Filter opties")
        
        # Filter de data voor alleen de A350H en A321H
        a350_data = A350H.reset_index()
        a321_data = A321H.reset_index()

        # Combineer de data voor beide vliegtuigen
        combined_data = pd.concat([ 
            a350_data.melt(id_vars=['index'], value_vars=['Hoogte (ft)', 'kts']).assign(Vliegtuig='A350'),
            a321_data.melt(id_vars=['index'], value_vars=['Hoogte (ft)', 'kts']).assign(Vliegtuig='A321')
        ])

        # Maak een plot met snelheid en hoogte van de A350H en A321H
        fig = px.line(
            combined_data,
            x='index',
            y='value',
            color='variable',
            line_dash='Vliegtuig',
            labels={'value': 'Waarde', 'index': 'Tijd (index)', 'variable': 'Variabele', 'Vliegtuig': 'Vliegtuig'},
            title='Hoogte en Snelheid van de A350 en A321',
            height=280
        )

        # Pas de y-as aan zodat de schaal van TRUE AIRSPEED (kts) beter past
        fig.update_layout(
            yaxis=dict(
                title='Hoogte (ft)',
                side='left'
            ),
            yaxis2=dict(
                title='Snelheid (kts)',
                overlaying='y',
                side='right'
            ),
            legend_title_text='Metingen',
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-2,  # Adjusted to place the legend 10 cm (approximately) below the plot
                xanchor="center",
                x=0.5
            ),
            margin=dict(b=100)  # Add bottom margin to ensure space for the legend
        )

        # Pas de namen in de legende aan
        fig.for_each_trace(lambda t: t.update(name=f"{t.name} ({t.legendgroup})") if t.legendgroup in ['A350', 'A321'] else None)

        # Voeg de tweede y-as toe voor TRUE AIRSPEED (kts)
        fig.for_each_trace(lambda t: t.update(yaxis='y2') if 'kts' in t.name else None)

        st.plotly_chart(fig)
        
        st.markdown(
            """
            <style>
            .sticky-legend {
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            background-color: white;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            z-index: 1000;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="sticky-legend">
            <h4>Legenda</h4>
            <h5>Hoogte (ft):</h5>
            <p><span style="color:purple">●</span> > 40,000 ft</p>
            <p><span style="color:blue">●</span> 30,000-40,000 ft</p>
            <p><span style="color:dodgerblue">●</span> 20,000-30,000 ft</p>
            <p><span style="color:lawngreen">●</span> 10,000-20,000 ft</p>
            <p><span style="color:greenyellow">●</span> 8,000-10,000 ft</p>
            <p><span style="color:yellow">●</span> 4,000-8,000 ft</p>
            <p><span style="color:gold">●</span> 2,000-4,000 ft</p>
            <h5>Geluidsmetingen (dB):</h5>
            <p><span style="color:blue">●</span> < 65 dB (Zeer laag)</p>
            <p><span style="color:green">●</span> 65-70 dB (Laag)</p>
            <p><span style="color:yellow">●</span> 70-75 dB (Gemiddeld)</p>
            <p><span style="color:orange">●</span> 75-80 dB (Hoog)</p>
            <p><span style="color:red">●</span> > 80 dB (Zeer hoog)</p>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:
        # Navigatie opties
        if 'page' not in st.session_state:
            st.session_state.page = "Klein vliegtuig"  # Default page

        def render_navigation():
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Klein vliegtuig'):
                    st.session_state.page = 'Klein vliegtuig'
            with col2:
                if st.button('Groot vliegtuig'):
                    st.session_state.page = 'Groot vliegtuig'

        # Navigation content
        render_navigation()  # Always render navigation first

        if st.session_state.page == "Klein vliegtuig":
            st.title("Klein vliegtuig")
            st.write("Data over kleine vliegtuigen!")
            flightdata = A321H  # Klein vliegtuig data
        elif st.session_state.page == "Groot vliegtuig":
            st.title("Groot vliegtuig")
            st.write("Data over grote vliegtuigen!")
            flightdata = A350H  # Groot vliegtuig data

        # Kleur voor de hoogte
        def flkleur(hoogte):
            if hoogte > 40000:
                return 'purple'
            elif hoogte > 30000:
                return 'blue'
            elif hoogte > 20000:
                return 'dodgerblue'
            elif hoogte > 10000:
                return 'lawngreen'
            elif hoogte > 8000:
                return 'greenyellow'
            elif hoogte > 4000:
                return 'yellow'
            elif hoogte > 2000:
                return 'gold'

        # Zorg ervoor dat 'kts' numeriek is
        flightdata.loc[:, 'kts'] = pd.to_numeric(flightdata['kts'], errors='coerce')

        # Functie om de kaart te maken en weer te geven
        def create_map(flightdata):
            m = folium.Map(location=[56.594560, 14.274343], zoom_start=5)
            folium.TileLayer(tiles="cartodbpositron", name="Grijze kaart").add_to(m)

            for i in flightdata.index:
                if not pd.isna(flightdata.loc[i, "Latitude"]) and not pd.isna(flightdata.loc[i, "Longitude"]):
                    folium.Circle(
                        location=[flightdata.loc[i, "Latitude"], flightdata.loc[i, "Longitude"]],
                        popup=f"Heading: {str(flightdata.loc[i, 'Richting'])}, Speed: {str(flightdata.loc[i, 'kts'])}, Hoogte: {str(flightdata.loc[i, 'Hoogte (ft)'])}",
                        color=flkleur(flightdata.loc[i, "Hoogte (ft)"]),
                        fill=True,
                        fill_color=flkleur(flightdata.loc[i, "Hoogte (ft)"]),
                        radius=500
                    ).add_to(m)
            return m

        # Maak en toon de kaart voor de geselecteerde vluchtdata
        map_object = create_map(flightdata)
        st_folium(map_object, width=1000, height=500)
        
        # Titel van de app
        st.title("Vliegtuiggeluidsmetingen rond Schiphol")

        # Gebruik de bestaande navigatieknoppen voor vliegtuigtype selectie
        if st.session_state.page == "Klein vliegtuig":
            data = pd.read_csv("A321.csv")
        elif st.session_state.page == "Groot vliegtuig":
            data = pd.read_csv("A350.csv")

        # Groepeer en bereken statistieken
        stats_per_punt = data.groupby(['lat', 'lng']).agg(
            aantal_metingen=('SEL_dB', 'count'),
            som_SEL_db=('SEL_dB', 'sum'),
            gemiddeld_SEL_db=('SEL_dB', 'mean'),
            gemiddelde_afstand=("distance", "mean"),
            gemiddelde_tijd=("duration", "mean"),
            gemiddelde_hoogte=("altitude", "mean")
        ).reset_index()

        # Functie om kleur te bepalen
        def db_naar_kleur(dB):
            if dB < 65:
                return 'blue'  # Very low
            elif dB < 70:
                return 'green'  # Low
            elif dB < 75:
                return 'yellow'  # Medium
            elif dB < 80:
                return 'orange'  # High
            else:
                return 'red'  # Very high
        
        def get_radius(dB):
            if dB < 65:
                return 8  # Small radius
            elif dB < 70:
                return 13  # Medium-small radius
            elif dB < 75:
                return 18  # Medium radius
            elif dB < 80:
                return 23  # Medium-large radius
            else:
                return 28  # Large radius

        # Maak de kaart
        m = folium.Map(location=[52.254, 4.765], zoom_start=11)

        for _, row in stats_per_punt.iterrows():
            kleur = db_naar_kleur(row['gemiddeld_SEL_db'])
            popup = folium.Popup(f"""
            <table style="font-size: 13px;">
            <tr><td><b>Aantal metingen</b></td><td>{row['aantal_metingen']:.0f}</td></tr>
            <tr><td><b>Gemiddeld SEL</b></td><td>{row['gemiddeld_SEL_db']:.0f} dB</td></tr>
            <tr><td><b>Gemiddelde afstand</b></td><td>{row['gemiddelde_afstand']:.0f} m</td></tr>
            <tr><td><b>Gemiddelde tijd</b></td><td>{row['gemiddelde_tijd']:.0f} s</td></tr>
            <tr><td><b>Gemiddelde hoogte</b></td><td>{row['gemiddelde_hoogte']:.0f} m</td></tr>
            </table>
            """, max_width=250)

            folium.CircleMarker(
                location=(row['lat'], row['lng']),
                radius=get_radius(row['gemiddeld_SEL_db']),
                color=kleur,
                fill=True,
                fill_opacity=0.4,
                popup=popup
            ).add_to(m)
            
            for i in flightdata.index:
                if not pd.isna(flightdata.loc[i, "Latitude"]) and not pd.isna(flightdata.loc[i, "Longitude"]) and flightdata.loc[i, "kts"] <= 300:
                    folium.Circle(
                    location=[flightdata.loc[i, "Latitude"], flightdata.loc[i, "Longitude"]],
                    popup=f"Heading: {str(flightdata.loc[i, 'Richting'])}, Speed: {str(flightdata.loc[i, 'kts'])}, Hoogte: {str(flightdata.loc[i, 'Hoogte (ft)'])}",
                    color=flkleur(flightdata.loc[i, "Hoogte (ft)"]),
                    fill=True,
                    fill_color=flkleur(flightdata.loc[i, "Hoogte (ft)"]),
                    radius=500
            ).add_to(m)

        # Toon de kaart in Streamlit
        st_folium(m, width=1000, height=500)

# Tab 3
with tabs[2]:
    # Maak 2 kolommen: linker fake-sidebar en rechter content
    col1, col2 = st.columns([1, 3])

    with col2:
        # Filter de dataset voor FIN
        AY_callsign_df = Jaar[Jaar['callsign'].str.startswith('FIN', na=False)]

        # Bereken gemiddelden
        gemiddelde_SEL_dB_FIN = AY_callsign_df['SEL_dB'].mean()
        gemiddelde_SEL_dB_A321_FIN = AY_callsign_df[AY_callsign_df['icao_type'] == 'A321']['SEL_dB'].mean()
        gemiddelde_SEL_dB_A350_FIN = AY_callsign_df[AY_callsign_df['icao_type'] == 'A359']['SEL_dB'].mean()
        gemiddelde_SEL_dB_Jaar = Jaar['SEL_dB'].mean()
        gemiddelde_SEL_dB_A321 = Jaar[Jaar['icao_type'] == 'A321']['SEL_dB'].mean()
        gemiddelde_SEL_dB_A350 = Jaar[Jaar['icao_type'] == 'A359']['SEL_dB'].mean()

        # Streamlit-app
        st.title("Vergelijking van dB waarden")

        df_gemiddelden = pd.DataFrame({
            "Categorie": ["A321 binnen FIN", "A350 binnen FIN", "FIN (alle vliegtuigen)", "A321 (algemeen)", "A350 (algemeen)", "Jaar (alle vliegtuigen)"],
            "SEL_dB Gemiddelde": [gemiddelde_SEL_dB_A321_FIN, gemiddelde_SEL_dB_A350_FIN, gemiddelde_SEL_dB_FIN, gemiddelde_SEL_dB_A321, gemiddelde_SEL_dB_A350, gemiddelde_SEL_dB_Jaar]
        })

        # Visualisatie met Streamlit en Matplotlib
        st.subheader("Grafiek van dB gemiddelden")
        fig, ax = plt.subplots()
        ax.bar(df_gemiddelden['Categorie'], df_gemiddelden['SEL_dB Gemiddelde'], color='#0B1560')

        # Stel de y-as in zodat deze begint bij 70 en eindigt bij 76
        ax.set_ylim(68, 72)  # De bovengrens van de y-as is 76

        # Voeg labels en titel toe aan de grafiek
        ax.set_xlabel('Categorie')
        ax.set_ylabel('Gemiddelde dB')
        ax.set_title('Gemiddelde dB per Categorie op punt Ku')

        # Draai de x-as labels als ze moeilijk leesbaar zijn
        plt.xticks(rotation=45, ha='right')

        # Toon de grafiek in Streamlit
        st.pyplot(fig)

        # Bereken de verschillen en toon in tekst
        verschil_A321_FIN_A350_FIN = gemiddelde_SEL_dB_A321_FIN - gemiddelde_SEL_dB_A350_FIN
        verschil_A321_Jaar_A350_Jaar = gemiddelde_SEL_dB_A321 - gemiddelde_SEL_dB_A350
        verschil_FIN_Jaar = gemiddelde_SEL_dB_FIN - gemiddelde_SEL_dB_Jaar

        st.subheader("Verschillen in gemiddelde SEL_dB-waarden")

        # Toon de tekstuele verschillen
        st.write(f"Het gemiddelde dB voor A321 binnen FIN is {gemiddelde_SEL_dB_A321_FIN:.2f} dB, en voor A350 binnen FIN is het {gemiddelde_SEL_dB_A350_FIN:.2f} dB. "
                f"Het verschil is {verschil_A321_FIN_A350_FIN:.2f} dB in het voordeel van {'A321' if verschil_A321_FIN_A350_FIN > 0 else 'A350'}.")

        st.write(f"Het gemiddelde dB voor A321 (algemeen) is {gemiddelde_SEL_dB_A321:.2f} dB, en voor A350 (algemeen) is het {gemiddelde_SEL_dB_A350:.2f} dB. "
                f"Het verschil is {verschil_A321_Jaar_A350_Jaar:.2f} dB in het voordeel van {'A321' if verschil_A321_Jaar_A350_Jaar > 0 else 'A350'}.")

        st.write(f"Het gemiddelde dB voor alle vliegtuigen binnen FIN is {gemiddelde_SEL_dB_FIN:.2f} dB, en voor het gehele jaar (alle vliegtuigen) is het {gemiddelde_SEL_dB_Jaar:.2f} dB. "
                f"Het verschil is {verschil_FIN_Jaar:.2f} dB in het voordeel van {'FIN' if verschil_FIN_Jaar > 0 else 'Jaar'}.")
        
    with col1:
        # Add a legend to the top of the page that stays visible when scrolling
        st.write('test')
