import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np

#data import en manipulatie
A350H = pd.read_excel('A350H.xlsx')
A321H = pd.read_excel('A321H.xlsx')

A350H['Hoogte (ft)'] = A350H['Hoogte (m)'] * 3.28084
A321H['Hoogte (ft)'] = A321H['Hoogte (m)'] * 3.28084

Jaar = pd.read_csv('GeluidsmetingGoed_2024.csv',index_col=0)

st.set_page_config(layout="wide")

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
            <h1>Schiphol geluidsdashboard</h1>
            <h3>Gemaakt door Gem, Roel en Mariah</h3>
        </div>
    </div>
'''.format(st.image(image, use_container_width=False, output_format="PNG")), unsafe_allow_html=True)

# Hoofdtabs
tabs = st.tabs(["Home 🏠", "Route 🛫", "Geluid 🔊", "Voorspelling 📊","Per passagier 👤"])

# Tab 1
with tabs[0]:
    st.header("Home")
    st.write('Welkom op ons geluidsdashboard!')
    st.write('In dit dashboard hebben we een specifieke route van de luchtvaartmaatschappij Finnair geanalyseerd. Deze route is bijzonder interessant omdat Finnair hierop twee verschillende vliegtuigtypes inzet: de Airbus A321, een kleiner toestel, en de Airbus A350-900, een aanzienlijk groter vliegtuig.')
    st.write('Door deze twee toestellen met elkaar te vergelijken, kunnen we inzicht krijgen in de verschillen tussen een klein en een groot vliegtuig en de impact daarvan op het geluidsniveau per passagier. Dit helpt ons beter te begrijpen hoe factoren zoals vliegtuiggrootte en belading bijdragen aan de geluidshinder die wordt ervaren.')
    # Maak 2 kolommen: linker fake-sidebar en rechter content

    # Titel van de app
    st.title("Kaarten met geluidsmetingen A350 en A321")
    st.write('Hieronder zie je twee verschillende kaarten waarop het geluidsniveau op diverse meetpunten wordt weergegeven voor beide vliegtuigen. De grootte van de cirkel geeft de afstand weer tussen het vliegtuig en het meetpunt op het moment van de meting: hoe groter de cirkel, hoe verder het vliegtuig zich op dat moment van het meetpunt bevond.')
    # Maak 2 kolommen: linker fake-sidebar en rechter content
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(
            """
            <div class="sticky-legend" style="margin-top: 4cm;">
            <h4>Legenda</h4>
            <h5>Geluidsmetingen (dB):</h5>
            <p><span style="color:#33cc33">●</span> < 65 dB (Zeer laag)</p>
            <p><span style="color:#99cc00">●</span> 65-70 dB (Laag)</p>
            <p><span style="color:#ffcc00">●</span> 70-75 dB (Gemiddeld)</p>
            <p><span style="color:#ff6600">●</span> 75-80 dB (Hoog)</p>
            <p><span style="color:#ff0000">●</span> > 80 dB (Zeer hoog)</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="sticky-legend" style="margin-top: 7.3cm;">
            <h4>Legenda</h4>
            <h5>Geluidsmetingen (dB):</h5>
            <p><span style="color:#33cc33">●</span> < 65 dB (Zeer laag)</p>
            <p><span style="color:#99cc00">●</span> 65-70 dB (Laag)</p>
            <p><span style="color:#ffcc00">●</span> 70-75 dB (Gemiddeld)</p>
            <p><span style="color:#ff6600">●</span> 75-80 dB (Hoog)</p>
            <p><span style="color:#ff0000">●</span> > 80 dB (Zeer hoog)</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
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
    
    with col2:
        
        # Titel van de app
        st.title("Kaarten met geluidsmetingen A350 en A321")

        # Laad dataset
        @st.cache_data
        def load_data():
            # Laad en combineer de CSV-bestanden geluidsmeting_2024_1.csv t/m geluidsmeting_2024_7.csv
            dataframes = [pd.read_csv(f'Geluidsmeting_2024_{i}.csv') for i in range(1, 8)]
            return pd.concat(dataframes, ignore_index=True)

        geluid = load_data()

        a350 = geluid[geluid["icao_type"] == "A359"].copy()
        a321 = geluid[geluid["icao_type"] == "A321"].copy()

        def sel_naar_kleur(sel):
            if sel >= 80:
                return "#ff0000"  # rood
            elif sel >= 75:
                return "#ff6600"  # oranje
            elif sel >= 70:
                return "#ffcc00"  # geel
            elif sel >= 65:
                return "#99cc00"  # lichtgroen
            else:
                return "#33cc33"  # groen

        def bereken_stats(geluid):
            return geluid.groupby(['lat', 'lng']).agg(
                aantal_metingen=('SEL_dB', 'count'),
                gemiddeld_SEL_db=('SEL_dB', 'mean'),
                gemiddelde_afstand=('distance', 'mean'),
                gemiddelde_tijd=('duration', 'mean'),
                gemiddelde_hoogte=('altitude', 'mean')
                ).reset_index()
        
        a350_stats = bereken_stats(a350)
        a321_stats = bereken_stats(a321)
        
        a350_stats = a350.groupby(['lat', 'lng']).agg(
        aantal_metingen=('SEL_dB', 'count'),
        gemiddeld_SEL_db=('SEL_dB', 'mean'),
        gemiddelde_afstand=('distance', 'mean'),
        gemiddelde_tijd=('duration', 'mean'),
        gemiddelde_hoogte=('altitude', 'mean')
        ).reset_index()

        def maak_folium_kaart(df_stats, toestelnaam):
            kaart = folium.Map(location=[df_stats['lat'].mean(), df_stats['lng'].mean()], zoom_start=10)

            for _, row in df_stats.iterrows():
                kleur = sel_naar_kleur(row['gemiddeld_SEL_db'])
                popup_text = (
                    f"<b>{toestelnaam}</b><br>"
                    f"Aantal metingen: {row['aantal_metingen']}<br>"
                    f"Gemiddelde SEL: {row['gemiddeld_SEL_db']:.1f} dB<br>"
                    f"Gemiddelde afstand: {row['gemiddelde_afstand']:.0f} m<br>"
                    f"Gemiddelde hoogte: {row['gemiddelde_hoogte']:.0f} m"
                )

                folium.CircleMarker(
                    location=(row['lat'], row['lng']),
                    radius=max(3, row['gemiddelde_hoogte'] * 0.02),
                    color=kleur,
                    fill=True,
                    fill_color=kleur,
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_text, max_width=200),
                    tooltip = popup_text
                ).add_to(kaart)

            return kaart

        # Toon kaarten in Streamlit
        st.subheader("Kaart van A350 meetpunten")
        st_folium(maak_folium_kaart(a350_stats, "A350"), width=1300, height=500)

        st.subheader("Kaart van A321 meetpunten")
        st_folium(maak_folium_kaart(a321_stats, "A321"), width=1300, height=500)

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

        # Plot voor de A321
        a321_fig = px.line(
            a321_data.melt(id_vars=['index'], value_vars=['Hoogte (ft)', 'kts']),
            x='index',
            y='value',
            color='variable',
            labels={'value': 'Waarde', 'index': 'Tijd (index)', 'variable': 'Variabele'},
            title='A321 Hoogte en Snelheid',
            height=280
        )

        a321_fig.update_layout(
            yaxis=dict(
            title='Hoogte (ft)',
            side='left'
            ),
            yaxis2=dict(
            title='Snelheid (kts)',
            overlaying='y',
            side='right'
            ),
            legend=dict(
            title_text='Metingen',
            orientation='h',
            yanchor='top',
            y=-0.5,  # Plaats de legenda onder de plot
            xanchor='center',
            x=0.5
            ),
            margin=dict(b=50)
        )

        a321_fig.for_each_trace(lambda t: t.update(yaxis='y2') if 'kts' in t.name else None)
        st.plotly_chart(a321_fig)

        # Plot voor de A350
        a350_fig = px.line(
            a350_data.melt(id_vars=['index'], value_vars=['Hoogte (ft)', 'kts']),
            x='index',
            y='value',
            color='variable',
            labels={'value': 'Waarde', 'index': 'Tijd (index)', 'variable': 'Variabele'},
            title='A350 Hoogte en Snelheid',
            height=280
        )

        a350_fig.update_layout(
            yaxis=dict(
            title='Hoogte (ft)',
            side='left'
            ),
            yaxis2=dict(
            title='Snelheid (kts)',
            overlaying='y',
            side='right'
            ),
            legend=dict(
            title_text='Metingen',
            orientation='h',
            yanchor='top',
            y=-0.5,  # Plaats de legenda onder de plot
            xanchor='center',
            x=0.5
            ),
            margin=dict(b=50)
        )

        a350_fig.for_each_trace(lambda t: t.update(yaxis='y2') if 'kts' in t.name else None)
        st.plotly_chart(a350_fig)

        # Legenda onder de kaart
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
            <p><span style="color:#33cc33">●</span> < 65 dB (Zeer laag)</p>
            <p><span style="color:#99cc00">●</span> 65-70 dB (Laag)</p>
            <p><span style="color:#ffcc00">●</span> 70-75 dB (Gemiddeld)</p>
            <p><span style="color:#ff6600">●</span> 75-80 dB (Hoog)</p>
            <p><span style="color:#ff0000">●</span> > 80 dB (Zeer hoog)</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
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

    with col2:
        # Navigatie opties
        if 'page' not in st.session_state:
            st.session_state.page = "Klein vliegtuig"  # Default page

        def render_navigation():
            col1, col2 = st.columns(2)
            with col1:
                if st.button('A321'):
                    st.session_state.page = 'Klein vliegtuig'
            with col2:
                if st.button('A350'):
                    st.session_state.page = 'Groot vliegtuig'

        # Navigation content
        render_navigation()  # Always render navigation first

        if st.session_state.page == "Klein vliegtuig":
            st.title("A321")
            st.write("De vlucht van de Airbus A321 van Finnair naar Helsinki is een typisch voorbeeld van hoe vliegtuigvluchten worden geanalyseerd om de impact op geluid en hoogte beter te begrijpen. Op de onderstaande kaart is de route van de A321 weergegeven, waarbij de hoogte op verschillende punten van de vlucht visueel wordt weergegeven door middel van kleuren. Het is duidelijk te zien hoe het vliegtuig door verschillende luchtlagen beweegt tijdens de reis naar Helsinki.")
            st.write('Een bijzonder interessante data-analyse komt van de geluidsmetingen tijdens het opstijgen van de A321. Deze geluidsdata is geplot op de locaties van de geluidsstations langs de vluchtroute. Elk punt op de kaart vertegenwoordigt een geluidsmeting die op dat moment werd vastgelegd. De grootte en kleur van de punten geven een gedetailleerd beeld van hoe luid het geluid was op verschillende plaatsen. Hoe groter en feller gekleurd de punten zijn, hoe hoger het geluidsniveau dat door het vliegtuig werd geproduceerd. Dit biedt inzicht in de geluidsbelasting rondom luchthavens en op de grond tijdens de cruciale fase van het opstijgen.')
            st.write('Deze combinatie van vluchtgegevens en geluidsmetingen helpt bij het begrijpen van de relatie tussen vlieghoogte, geluidsoverlast en de impact van luchtverkeer op de omgeving, wat essentieel is voor het verbeteren van luchthavengeluidbeheer en het minimaliseren van overlast voor omwonenden.')
            flightdata = A321H  # Klein vliegtuig data
        elif st.session_state.page == "Groot vliegtuig":
            st.title("A350")
            st.write("De vlucht van de Airbus A350-900 (A359) van Finnair naar Helsinki biedt een waardevolle gelegenheid om de impact van moderne vliegtuigen op hoogte en geluidsniveaus beter te begrijpen. Op de onderstaande kaart is de route van de A350 weergegeven, waarbij de hoogte op verschillende punten van de vlucht visueel wordt weergegeven door middel van kleuren. Dit laat zien hoe het vliegtuig zich door verschillende luchtlagen beweegt tijdens zijn reis naar Helsinki.")
            st.write('Een interessante dataset komt van de geluidsmetingen tijdens het opstijgen van de A350. Deze geluidsdata is geplot op de locaties van de geluidsstations langs de vluchtroute. Elk punt op de kaart vertegenwoordigt een meting van het geluidsniveau op dat specifieke moment. De grootte en kleur van de punten geven duidelijk aan hoe luid het geluid was op verschillende locaties. Hoe groter en intenser de kleur van de punten, hoe hoger het geluidsniveau dat door het vliegtuig werd geproduceerd. Dit biedt waardevolle inzichten in de geluidsimpact van de A350-900, vooral tijdens de opstijgfase, en helpt om de geluidsoverlast in de omgeving van luchthavens beter te begrijpen.')
            st.write('De combinatie van vluchtgegevens en geluidsmetingen biedt een gedetailleerd overzicht van de relatie tussen vlieghoogte, geluidsoverlast en de effecten van luchtverkeer op de omliggende gebieden. Dit is cruciaal voor het optimaliseren van luchtvaartbeheer en het verminderen van geluidsoverlast voor omwonenden, vooral bij luchthavens die veelvuldig gebruik maken van de A350-900.')
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
            folium.TileLayer(tiles="OpenStreetMap", name="Blauwe kaart").add_to(m)

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
            kleur = sel_naar_kleur(row['gemiddeld_SEL_db'])
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

    # Titel van de app
    st.title("Hoe presteert Finnair qua geluid op Schiphol Airport?")
    st.write('Er is een analyse uitgevoerd om het geluidsniveau van Finnair-vliegtuigen te vergelijken met andere luchtvaartmaatschappijen op Schiphol Airport. Hierbij is specifiek gekeken naar de Airbus A321, de Airbus A350 en alle vliegtuigen samen. In het linkermenu kan een meetpunt worden geselecteerd om te zien hoe het geluid zich op verschillende locaties gedraagt.')
    st.write('Uit de analyse blijkt een verschil tussen de vliegtuigen van Finnair en die van andere maatschappijen. Dit kan meerdere oorzaken hebben. Een belangrijke factor is dat Finnair-vliegtuigen mogelijk vaker geland zijn dan opgestegen op bepaalde banen. Aangezien een vliegtuig meer geluid produceert bij het opstijgen dan bij het landen, kan dit de verschillen in gemeten geluidsniveaus verklaren.')
    st.write('Een andere mogelijke oorzaak is de afstand tot het meetpunt. Hoe dichter een vliegtuig bij het meetpunt vliegt, hoe hoger het gemeten geluidsniveau. Om dit te onderzoeken, is een lijn toegevoegd aan de grafieken. In de eerste grafiek laat deze lijn zien hoe ver het vliegtuig van het meetpunt verwijderd was. In de tweede grafiek wordt de hoogte van het vliegtuig weergegeven. Bij de meeste meetpunten is duidelijk te zien dat zowel de hoogte als de afstand invloed heeft op het gemeten geluidsniveau.')
    st.write('Daarnaast is er een vergelijking gemaakt tussen de Airbus A321 en de Airbus A350 van Finnair. Hierbij werd echter geen significant verschil in geluidsniveau waargenomen tussen deze twee vliegtuigtypen.')
    
    # Voeg een nieuwe kolom toe met de gecombineerde locatie en bron
    geluid["locatie_bron"] = geluid["location_long"] + ", " + geluid["bron"]

    def bereken_y_limieten(df):
        min_sel = df.groupby("location_long")["SEL_dB"].mean().min()
        max_sel = df.groupby("location_long")["SEL_dB"].mean().max()
        min_dist = df.groupby("location_long")["distance"].mean().min()
        max_dist = df.groupby("location_long")["distance"].mean().max()
        min_alt = df.groupby("location_long")["altitude"].mean().min()
        max_alt = df.groupby("location_long")["altitude"].mean().max()
        return np.floor(min_sel), np.ceil(max_sel), np.floor(min_dist), np.ceil(max_dist), np.floor(min_alt), np.ceil(max_alt)

    y_min_sel, y_max_sel, y_min_dist, y_max_dist, y_min_alt, y_max_alt = bereken_y_limieten(geluid)

    # Verdeel de lay-out in twee kolommen: 1/4 (links) en 3/4 (rechts)
    col1, col2 = st.columns([1, 3])

    # Sidebar - Selecteer een locatie
    with col1:
        st.subheader("Filter op locatie en bron")

        # Voeg "Alle Locaties" toe aan de lijst van locaties
        locaties_bron = np.append(geluid["locatie_bron"].unique(), "Alle Locaties")

        # Dropdown maken met "Alle Locaties" als default
        geselecteerde_waarde = st.selectbox("Kies een locatie en bron:", locaties_bron, index=list(locaties_bron).index("Alle Locaties"))

        # Als de gebruiker "Alle Locaties" kiest, toon alle data
        if geselecteerde_waarde == "Alle Locaties":
            geluid_filtered = geluid
            locatie, bron = "Alle Locaties", "Alle Bronnen"
        else:
            # Filter de dataset op de gekozen locatie en bron
            locatie, bron = geselecteerde_waarde.split(", ")  # Splits de tekst
            geluid_filtered = geluid[(geluid["location_long"] == locatie) & (geluid["bron"] == bron)]

        # Toon de geselecteerde locatie en bron
        st.write(f"Toon data voor: **{locatie}** (Bron: **{bron}**)")

    # Filter dataset voor FIN-callsigns binnen de gekozen locatie
    geluid_FIN = geluid_filtered[geluid_filtered["callsign"].str.startswith("FIN", na=False)]
    geluid_ALL = geluid_filtered  # Bevat alle data voor deze locatie

    # Functie om gemiddelde SEL_dB, afstand en hoogte te berekenen
    def calc_avg(df):
        df_avg = df.groupby("icao_type", as_index=False).agg({"SEL_dB": "mean", "distance": "mean", "altitude": "mean"})
        all_avg = pd.DataFrame({"icao_type": ["ALL"], 
                                "SEL_dB": [df["SEL_dB"].mean()], 
                                "distance": [df["distance"].mean()],
                                "altitude": [df["altitude"].mean()]})
        return pd.concat([df_avg[df_avg["icao_type"].isin(["A321", "A359"])], all_avg])

    # Bereken gemiddelden voor de gekozen locatie en bron
    df_final_FIN = calc_avg(geluid_FIN).rename(columns={"SEL_dB": "SEL_dB_FIN", "distance": "Distance_FIN", "altitude": "Altitude_FIN"})
    df_final_ALL = calc_avg(geluid_ALL).rename(columns={"SEL_dB": "SEL_dB_ALL", "distance": "Distance_ALL", "altitude": "Altitude_ALL"})

    # Combineer de datasets
    df_combined = df_final_FIN.merge(df_final_ALL, on="icao_type", how="outer").round(2)

    # Maak de grafiek met dubbele y-as voor SEL_dB en afstand
    fig_dist = go.Figure()

    # Balken voor SEL_dB (eerste y-as)
    fig_dist.add_trace(go.Bar(x=df_combined["icao_type"], y=df_combined["SEL_dB_FIN"], 
                            name="SEL dB FIN", yaxis="y1", marker_color="#0B1560", text=df_combined["SEL_dB_FIN"].round(2), textposition="auto"))

    fig_dist.add_trace(go.Bar(x=df_combined["icao_type"], y=df_combined["SEL_dB_ALL"], 
                            name="SEL dB ALL", yaxis="y1", marker_color="#8B0000", text=df_combined["SEL_dB_ALL"], textposition="auto"))

    # Lijnen voor afstand (tweede y-as)
    fig_dist.add_trace(go.Scatter(x=df_combined["icao_type"], y=df_combined["Distance_FIN"], 
                                name="Afstand FIN", yaxis="y2", mode="lines+markers", marker=dict(color="blue")))

    fig_dist.add_trace(go.Scatter(x=df_combined["icao_type"], y=df_combined["Distance_ALL"], 
                                name="Afstand ALL", yaxis="y2", mode="lines+markers", marker=dict(color="red")))

    # Layout aanpassen voor de eerste grafiek (SEL_dB en afstand)
    fig_dist.update_layout(
        title=f"Gemiddelde dB en Afstand per Vliegtuigtype ({locatie}, {bron})",
        xaxis=dict(title="ICAO Type"),
        yaxis=dict(title="Gemiddelde dB (dB)", range=[y_min_sel, y_max_sel]),
        yaxis2=dict(title="Gemiddelde Afstand (m)", range=[y_min_dist, y_max_dist], overlaying="y", side="right"),
        legend=dict(x=0, y=1),
        barmode="group"
    )

    # Maak de grafiek met dubbele y-as voor SEL_dB en hoogte
    fig_alt = go.Figure()

    # Balken voor SEL_dB (eerste y-as)
    fig_alt.add_trace(go.Bar(x=df_combined["icao_type"], y=df_combined["SEL_dB_FIN"], 
                            name="SEL dB FIN", yaxis="y1", marker_color="#0B1560", text=df_combined["SEL_dB_FIN"], textposition="auto"))

    fig_alt.add_trace(go.Bar(x=df_combined["icao_type"], y=df_combined["SEL_dB_ALL"], 
                            name="SEL dB ALL", yaxis="y1", marker_color="#8B0000", text=df_combined["SEL_dB_ALL"], textposition="auto"))

    # Lijnen voor hoogte (tweede y-as)
    fig_alt.add_trace(go.Scatter(x=df_combined["icao_type"], y=df_combined["Altitude_FIN"], 
                                name="Hoogte FIN", yaxis="y2", mode="lines+markers", marker=dict(color="blue")))

    fig_alt.add_trace(go.Scatter(x=df_combined["icao_type"], y=df_combined["Altitude_ALL"], 
                                name="Hoogte ALL", yaxis="y2", mode="lines+markers", marker=dict(color="red")))

    # Layout aanpassen voor de tweede grafiek (SEL_dB en hoogte)
    fig_alt.update_layout(
        title=f"Gemiddelde dB en Hoogte per Vliegtuigtype ({locatie}, {bron})",
        xaxis=dict(title="ICAO Type"),
        yaxis=dict(title="Gemiddelde dB (dB)", range=[y_min_sel, y_max_sel]),
        yaxis2=dict(title="Gemiddelde Hoogte (m)", range=[y_min_alt, y_max_alt], overlaying="y", side="right"),
        legend=dict(x=0, y=1),
        barmode="group"
    )

    # Toon de grafieken onder elkaar in de rechter kolom
    with col2:
        st.plotly_chart(fig_dist, use_container_width=True)  # Grafiek met Geluid en Afstand
        st.plotly_chart(fig_alt, use_container_width=True)   # Grafiek met Geluid en Hoogte
    
    a350 = geluid[geluid["icao_type"] == "A359"]
    a321 = geluid[geluid["icao_type"] == "A321"]

    grouped_a350 = a350.groupby("location_short")["SEL_dB"].mean().sort_values(ascending=False)
    grouped_a321 = a321.groupby("location_short")["SEL_dB"].mean().sort_values(ascending=False)

    combined_df = pd.DataFrame({
        "A350": grouped_a350,
        "A321": grouped_a321
    })

    # Top 5 locaties o.b.v. gemiddelde SEL
    top5_locations = combined_df.mean(axis=1).sort_values(ascending=False).head(5)
    top5_df = combined_df.loc[top5_locations.index]

    # Plotly bar chart
    fig = go.Figure(data=[
        go.Bar(name='A350', x=top5_df.index, y=top5_df["A350"]),
        go.Bar(name='A321', x=top5_df.index, y=top5_df["A321"])
    ])

    fig.update_layout(
        title="Top 5 locaties: Gemiddeld SEL (A350 vs A321)",
        xaxis_title="Locatie",
        yaxis_title="Gemiddelde SEL (dB)",
        barmode='group'
    )
    st.subheader("Top 5 meetpunten met meeste geluid")

    # Streamlit output
    st.title("Vergelijking van Gemiddeld SEL (A350 vs A321)")
    st.plotly_chart(fig)
        
with tabs[3]:
    # Modelcoëfficiënten voor Airbus A321
    a321_coefficients = {
        "passagiers": 0.00000000e+00,
        "belading": 6.68410639e-16,
        "altitude": -2.21200409e-03,
        "windspeed": 3.53188408e-01,
        "winddirection": -2.14568430e-04,
        "intercept": 75.23782155858513
    }

    # Modelcoëfficiënten voor Airbus A350-900 (A359)
    a350_coefficients = {
        "passagiers": 0.00000000e+00,
        "belading": -3.69496100e-16,
        "altitude": -2.20477636e-03,
        "windspeed": 4.45607993e-01,
        "winddirection": 1.65114663e-04,
        "intercept": 74.50187813423753
    }

    # Streamlit-app
    st.title("Voorspelling van geluidsniveau (dB)")

    # Dropdown-menu voor vliegtuigkeuze
    vliegtuig_optie = st.selectbox("Kies een vliegtuigtype:", ["A321", "A350-900"])

    # Modelcoëfficiënten laden op basis van keuze
    if vliegtuig_optie == "A321":
        coefficients = a321_coefficients
    else:
        coefficients = a350_coefficients

    # Inputvelden voor variabelen
    passagiers = st.number_input("Aantal passagiers", min_value=0, max_value=300, value=160)
    belading = st.number_input("Belading (kg)", min_value=0, max_value=20000, value=6000)
    altitude = st.number_input("Hoogte (ft)", min_value=0, max_value=40000, value=10000)
    windspeed = st.number_input("Windsnelheid (knots)", min_value=0, max_value=100, value=10)
    winddirection = st.number_input("Windrichting (graden)", min_value=0, max_value=360, value=180)

    # Geluid voorspellen
    if st.button("Voorspel geluidsniveau"):
        voorspelling = (coefficients["intercept"] +
                        coefficients["passagiers"] * passagiers +
                        coefficients["belading"] * belading +
                        coefficients["altitude"] * altitude +
                        coefficients["windspeed"] * windspeed +
                        coefficients["winddirection"] * winddirection)
        st.write(f"**Voorspeld geluidsniveau (dB): {voorspelling:.2f} dB**")

with tabs[4]:
    kaart = pd.read_csv("gem_geluid_locatie.csv")


    # --- Sidebar controls ---
    st.title("📊 Geluidsniveau per passagier")

    st.write("Deze barplot laat zien wat de SEL_dB waarde per passagier is voor de A350 en de A321. Met de sliders kan de loadfactor worden aangepast. Op deze manier kan worden gekeken bij welke loadfactor welk vliegtuig voordeliger is.")

    # --- Zoekbare dropdown voor locatie ---
    location = st.selectbox(
        "🔍 Kies een locatie:",
        sorted(kaart["location_short"].unique()),
        index=0
    )

    # --- Aparte sliders per vliegtuigtype ---
    st.markdown("### 🎯 Loadfactor per vliegtuigtype")
    lf_a321_percent = st.slider("A321 Loadfactor (%)", 5, 100, 80, 1, format="%d%%")
    lf_a350_percent = st.slider("A350 Loadfactor (%)", 5, 100, 80, 1, format="%d%%")

    # Omzetten naar decimale waarde
    lf_a321 = lf_a321_percent / 100
    lf_a350 = lf_a350_percent / 100

    # --- Filter op locatie ---
    filtered = kaart[kaart["location_short"] == location].copy()

    # --- Voeg kolom toe voor loadfactor per vliegtuigtype ---
    def get_loadfactor(row):
        if row["icao_type"] == "A321":
            return lf_a321
        elif row["icao_type"] == "A350":
            return lf_a350
        else:
            return 1.0  # fallback

    filtered["loadfactor"] = filtered.apply(get_loadfactor, axis=1)
    filtered["dB_per_passenger"] = filtered["SEL_dB"] / (filtered["seats"] * filtered["loadfactor"])

    # --- Plot ---
    fig = px.bar(
        filtered,
        x="icao_type",
        y="dB_per_passenger",
        color="icao_type",
        labels={"dB_per_passenger": "SEL_dB per passagier"},
        title=f"Geluidsniveau per passagier - {location} (A321: {lf_a321_percent}%, A350: {lf_a350_percent}%)"
    )

    fig.update_layout(
        yaxis_title = "SEL_dB per passagier",
        xaxis_title = "Vliegtuigtype",
        legend_title_text="Vliegtuigtype"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bereken bezette stoelen op basis van loadfactor
    a321_seats = filtered[filtered["icao_type"] == "A321"]["seats"].iloc[0] if "A321" in filtered["icao_type"].values else 0
    a350_seats = filtered[filtered["icao_type"] == "A350"]["seats"].iloc[0] if "A350" in filtered["icao_type"].values else 0

    a321_occupied = int(a321_seats * lf_a321)
    a350_occupied = int(a350_seats * lf_a350)

    # Toon widgets onder de grafiek
    st.markdown("### ✈️ Bezetting per vliegtuigtype")
    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="A321 bezette stoelen", value=f"{a321_occupied} van {a321_seats}")

    with col2:
        st.metric(label="A350 bezette stoelen", value=f"{a350_occupied} van {a350_seats}")

