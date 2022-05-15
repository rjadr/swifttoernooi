import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from PIL import Image
import geopandas as gpd
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from streamlit_cookies_manager import EncryptedCookieManager
from shapely.geometry import Point

st.set_page_config(page_title='Swift Hemelvaartsdagtoernooi', page_icon="favicon.ico", layout="wide")
# This should be on top of your script
cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="rjadr/streamlit-cookies-manager/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password='mypassword' #os.environ.get("COOKIES_PASSWORD", "My secret password"),
)


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown('<link href="https://fonts.cdnfonts.com/css/cooper-black" rel="stylesheet">', unsafe_allow_html = True)

with st.sidebar:
    choose = option_menu("kv Swift Hemelvaartsdagtoernooi", ["Welkom", "Toernooi-informatie", "Wedstrijdschema", "Standen", "Plattegrond", "Wedstrijdreglement", "Turf War"],
                         icons=['house', 'info-circle', 'calendar3', 'trophy', 'map', 'journal-check', 'flag'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#FF9900"},
    }, orientation="vertical",
    )

### GET DATA ###
#https://docs.streamlit.io/knowledge-base/tutorials/databases/public-gsheet
#https://towardsdatascience.com/make-dataframes-interactive-in-streamlit-c3d0c4f84ccb

@st.cache(ttl=300) # 5 minute cache
def get_data():
    sheet_id = "1zLobPdXuW9RDJwPD0f3m0QHl-7Vb2eK2gqNKFwmNXvE"
    url_stand = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Standen"
    stand = pd.read_csv(url_stand, skiprows=1, usecols=[0,1,2,3,4,5,6,7], names=['Poule','Team','Voor','Tegen','Doelsaldo','Gespeeld','Punten','Stand'])

    url_schema = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Speelschema"
    schema = pd.read_csv(url_schema, usecols=list(range(0,10)))
    schema['Score uit'] = schema['Score uit'].astype('Int64')
    schema['Score thuis'] = schema['Score thuis'].astype('Int64')

    return stand, schema

stand, schema = get_data()

################

logoswift = Image.open('swiftlogo.png')
plattegrond = Image.open('plattegrond_hemelvaart.jpg')

if choose == "Welkom":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:  # To display the header text using css style
        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
        </style> """, unsafe_allow_html=True)
        st.markdown('<p class="font">Welkom!</p>', unsafe_allow_html=True)
    with col2:  # To display brand log
        st.image(logoswift, width=130)

    st.markdown("Het is weer zo ver, voor de 72e keer in de geschiedenis van Swift vindt het kv Swift Hemelvaartsdagtoernooi plaats! Op het moment van het schrijven van dit voorwoord hebben 14 verenigingen en 92 teams aangemeld. Heel erg fijn dat zoveel sporters naar Swift komen om te genieten van dit jaarlijkse toernooi!\n\nOp deze site vindt u alle informatie over het toernooi. U kunt o.a. het wedstrijdschema, de standen, de plattegrond en het wedstrijdreglement bekijken. Browst u mobiel? Klik dan op de pijl linksboven om het menu te zien.\n\nWe wensen u een mooi toernooi toe!\n\nVriendelijke groet,\n\nDe toernooicommissie van het kv Swift Hemelvaartsdagtoernooi")

if choose == "Toernooi-informatie":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Toernooi-informatie</p>', unsafe_allow_html=True)


    st.markdown("Hieronder vindt u praktische informatie over de toernooidag:\n\n### Programma")
    table = {'Tijd': {0: '10:00',
                    1: '10:30',
                    2: '11:00',
                    3: '11:30',
                    4: '12:00',
                    5: '12:30',
                    6: '13:00',
                    7: '13:30',
                    8: '14:00',
                    9: '14:30',
                    10: '15:00',
                    11: '15:30',
                    12: '16:10'},
     'Kinderprogramma (Kangoeroes, F, E, D)': {0: 'Opening toernooi met warming up op hoofdveld Swift',
                                               1: 'Schminken, Tekenen, Springkussen',
                                               2: 'Schminken, Tekenen, Springkussen',
                                               3: 'Schminken, Tekenen, Springkussen',
                                               4: 'Springkussen',
                                               5: 'Springkussen',
                                               6: 'Spelletjesparcours, Springkussen',
                                               7: 'Spelletjesparcours, Springkussen',
                                               8: 'Spelletjesparcours, Springkussen',
                                               9: 'Spelletjesparcours, Springkussen',
                                               10: 'Springkussen',
                                               11: 'Springkussen',
                                               12: ' '},
     'Toernooi': {0: 'Opening toernooi met warming up op hoofdveld Swift',
                  1: 'Ronde 1',
                  2: 'Ronde 2',
                  3: 'Ronde 3',
                  4: 'Ronde 4',
                  5: 'Ronde 5',
                  6: 'Ronde 6',
                  7: 'Ronde 7',
                  8: 'Ronde 8',
                  9: 'Ronde 9',
                  10: 'Ronde 10',
                  11: 'Ronde 11',
                  12: 'Prijsuitreiking'}}

    st.table(pd.DataFrame(table))
    st.markdown("### Parkeren\n\nParkeren met de auto is mogelijk op het parkeerterrein van Sportpark de Sprong. Fietsers verzoeken wij de fiets te parkeren in de fietsenrekken voor de ingang van de sporthal en niet bij (de toegangsweg naar) het clubhuis.\nDe toegangsweg naar het complex is niet voor autoverkeer toegankelijk en dient vrij gehouden te worden voor de hulpdiensten.\n\n### Aankomst/melden\n\nWij verzoeken teams dringend op tijd aanwezig te zijn en zich uiterlijk om 10:00 uur te melden bij de wedstrijdleiding (bij het materialenhok naast het clubhuis, zie plattegrond). We wijzen erop dat het niet mogelijk is een wedstrijd op een later tijdstip te spelen. Zie punt 4 van het wedstrijdreglement.\n\nDe terreinen zijn toegankelijk vanaf 9 uur 's morgens.\n\n### Kinderactiviteiten\n\nNaast de wedstrijden dit jaar extra activiteiten voor de jeugd. Het toernooi zal geopend worden met een muzikale warming-up waarbij iedereen zich klaar kan maken voor een sportieve dag. Alle spelende en niet-spelende jeugd kan meedoen, maar ook senioren die een extra warming-up nodig hebben zijn meer dan welkom om aan te sluiten. Verder kun je je dit jaar laten schminken en een sprongetje wagen op het springkussen. In de middag vinden er spelletjes plaats voor de jonge jeugd. Voltooi alle spellen en krijg een kleine beloning! Neem je broertjes, zusjes, vriendjes en vriendinnetjes mee om samen tussen de wedstrijden door te spelen.\n\nHiernaast is het spel Turf War te spelen via [https://hemelvaart.kvswift.nl](https://hemelvaart.kvswift.nl). Wie verovert Sportpark de Sprong namens zijn club? Check met je mobiel in op zoveel mogelijk locaties op het sportpark. De club die het langst zoveel mogelijk locaties in bezit houdt wint de Turf War!\n\n### Afval\n\nVoor afval treft u zowel bij de kleedruimten, kantine als op het veld speciale afvalbakken aan. Men wordt dringend verzorgd deze te gebruiken!\n\n### EHBO\n\nDe EHBO-post bevindt zich bij de kleedkamers naast het clubhuis.\n\n### Prijzen\n\nVoor elke afdeling is één prijs beschikbaar. De prijsuitreiking vindt plaats om ??? uur bij ???. Voor de D,E en F-jeugd is er voor ieder kind een vaantje beschikbaar, deze kunnen vanaf 12.00 uur door de coaches opgehaald worden bij de wedstrijdleiding.\n\n### (Kunst)grasvelden\n\nVelden S4 (senioren), E1, E2, E3, F1 en F2 zijn gelegen op de kunstgrasvelden. Alle andere velden op natuurgras. Zie het wedstrijdschema om te kijken op welke velden je speelt.\n\n### Fluiten\n\nNa aankomst ontvangt u de wedstrijdbriefjes met de te fluiten wedstrijden. Wilt u de uitslagen z.s.m. na afloop van de wedstrijd doorgeven bij de wedstrijdleiding? De scheidsrechters geven de bal door aan de volgende scheidsrechter, tenzij op het briefje verzocht wordt de bal bij de leiding in te leveren.\n\n### Overig\n\nK.v. Swift stelt zich niet aansprakelijk voor het zoekraken of beschadigen van eigendommen. Het is de deelnemende verenigingen niet toegestaan tijdens het toernooi verkoopacties te houden op de velden.\n\n### Eten en drinken\n\nEten en drinken wordt afgerekend met consumptiebonnen die in het clubhuis te verkrijgen zijn. 's Middags zijn ze ook te koop bij het snoep/ijs.\n\n### Locatie en contact\n\nKorfbalvereniging Swift\n\nSportcomplex de Sprong\n\nDe Aanloop 5\n\n4335 AT Middelburg\n\nTel. 0118 850 437 (clubhuis)\n\ne-mail: [kvswifthemelvaart@gmail.com](mailto:kvswifthemelvaart@gmail.com)")
    st.map(data=pd.DataFrame([{'lat':51.497489353450895, 'lon':3.594653606414795}]))

if choose == "Wedstrijdschema":
    scheidsrechters = sorted(list(schema['Scheidsrechter'].drop_duplicates()))
    teams = sorted([i for i in np.unique(schema[['Thuis', 'Uit']]) if not i.startswith('No ') and not i.startswith('No.')])
    verenigingen = sorted(set([j[0] if (j := i.split(' ')) and len(str(j[-1])) <= 2 else i for i in teams]))
    poules = sorted(list(schema['Poule'].drop_duplicates()))
    rondes = sorted(list(schema['Ronde'].drop_duplicates()))

    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Wedstrijdschema</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        teams_choice = st.multiselect('Teams:', teams)
    with col2:
        verenigingen_choice = st.multiselect('Verenigingen:', verenigingen)
    with col1:
        poules_choice = st.multiselect('Poules:', poules)
    with col2:
        rondes_choice = st.multiselect('Rondes:', rondes)
    with col1:
        scheidsrechters_choice = st.multiselect('Scheidsrechters:', scheidsrechters)

    filters = {
        'teams_choice': teams_choice,
        'verenigingen_choice': verenigingen_choice,
        'poules_choice': poules_choice,
        'rondes_choice': rondes_choice,
        'scheidsrechters_choice': scheidsrechters_choice
    }

    def filter_df(filter_name, filter_value):
        if filter_name == 'teams_choice':
            poule_nrs = schema[schema[['Thuis', 'Uit']].isin(filter_value).any(axis=1)]['Poule'].unique()
            cross_finals_filter = (schema['Poule'].str.contains('|'.join(poule_nrs), na=False)) & (schema['Thuis'].str.startswith('No ') | schema['Thuis'].str.startswith('No.'))
            teams_filter = schema[['Thuis', 'Uit']].isin(filter_value).any(axis=1)
            return np.logical_or(teams_filter, cross_finals_filter)
        elif filter_name == 'verenigingen_choice':
            poule_nrs = schema[(schema['Thuis'] + ' ' + schema['Uit']).str.contains('|'.join(filter_value))]['Poule'].unique()
            cross_finals_filter = (schema['Poule'].str.contains('|'.join(poule_nrs), na=False)) & (schema['Thuis'].str.startswith('No ') | schema['Thuis'].str.startswith('No.'))
            teams_filter = (schema['Thuis'] + ' ' + schema['Uit']).str.contains('|'.join(filter_value))
            return np.logical_or(teams_filter, cross_finals_filter)
        elif filter_name == 'poules_choice':
            return schema['Poule'].isin(filter_value)
        elif filter_name == 'rondes_choice':
            return schema['Ronde'].isin(filter_value)
        elif filter_name == 'scheidsrechters_choice':
            return schema['Scheidsrechter'].isin(filter_value)
        else:
            return np.full(len(schema), True)

    #filter non empty items in filters
    filters = [filter_df(k,v) for k, v in filters.items() if v]
    filter_ = np.full(len(schema), True)
    filter_ = np.logical_and.reduce((filter_, *filters))

    df_schema = schema.copy()
    st.dataframe(df_schema[filter_].sort_values(["Ronde", "Poule"],
                                ascending=True).reset_index(drop=True))

if choose == "Standen":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Standen</p>', unsafe_allow_html=True)

  #  st.markdown('Kies poule of team om de standen te zien')

    # remove item from pandas series if startswith 'No ' or 'No.'
    teams = [i for i in stand['Team'].drop_duplicates().sort_values().to_list() if
             not i.startswith('No ') and not i.startswith('No.')]
   # poules = stand['Poule'].drop_duplicates().sort_values()

   # filters = {
   #     'teams_choice': st.selectbox(
   #         'Team:', options=teams),
       # 'poules_choice': st.selectbox(
       #     'Poule:', options=poules)
    #}

   # def filter_df(filter_name, filter_value):
   #     if filter_name == 'teams_choice':
   #         return stand['Poule'].eq(stand[stand['Team'] == filter_value]['Poule'].values[0])
    #    elif filter_name == 'poules_choice':
     #       return stand['Poule'].eq(filter_value)

    DEFAULT = '< KIES EEN TEAM >'

    def selectbox_with_default(text, values, default=DEFAULT, sidebar=False):
        func = st.sidebar.selectbox if sidebar else st.selectbox
        return func(text, np.insert(np.array(values, object), 0, default))

    team = selectbox_with_default('Team', teams)

    if team == DEFAULT:
        st.warning("Kies een team!")
        raise st.scriptrunner.StopException
    else:
        filter_ = stand['Poule'].eq(stand[stand['Team'] == team]['Poule'].values[0])
        df_stand = stand.copy()
        df_stand = df_stand[filter_].sort_values(["Stand"],
                                    ascending=True).reset_index(drop=True)
        df_stand.index = range(1, df_stand.shape[0] + 1)
        st.dataframe(df_stand[['Team', 'Voor', 'Tegen', 'Doelsaldo', 'Gespeeld', 'Punten']])

#    filters = [filter_df(k,v) for k, v in filters.items() if v]
 #   filter_ = np.full(len(schema), True)
 #   filter_ = np.logical_and.reduce((filter_, *filters))



if choose == "Plattegrond":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Plattegrond</p>', unsafe_allow_html=True)

    st.image(plattegrond, use_column_width=True)

if choose == "Wedstrijdreglement":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Wedstrijdreglement</p>', unsafe_allow_html=True)

    st.markdown("1. De wedstrijden worden gespeeld volgens de regels van de KNKV\n\n2. Elke wedstrijd duurt 25 (2x 12 1⁄2 ) minuten. Zowel het begin -, het rust- als het eindsignaal worden centraal gegeven. Bij pupillen (D,E & F) wordt er in de rust van functie (én niet van vak) gewisseld, ongeacht het aantal doelpunten. De E- en F-jeugd neemt eerst ieder 3 strafworpen, spelen tot het wissel- (bel)signaal, beginnen weer met ieder 3 strafworpen en spelen dan de wedstrijd uit. De strafworpen worden niet meegeteld voor de einduitslag. Na iedere ronde is er 5 minuten om te wisselen en op te stellen.\n\n3. De eerstgenoemde ploeg in het programma heeft de vakkeuze en neemt de bal uit\n\n4. Een team dat bij de rust nog niet gereed is wordt geacht niet te zijn opgekomen. De uitslag wordt dan 3-0 in het voordeel van de tegenpartij.\n\n5. In afdelingen van vier ploegen wordt de stand opgemaakt na een halve competitie en volgt daarna de finale-wedstrijd en de strijd om de 3e plaats. De winnaar van de finale-wedstrijd is kampioen in de afdeling. Bij een gelijkspel in een finale-wedstrijd telt regel 6 (zie hieronder) In afdelingen van 5 of 6 teams wordt géén finale gespeeld.\n\n6. De plaatsing van de ploegen in de eindrangschikking wordt bepaald door:\n\n    1. Het aantal wedstrijdpunten\n\n    2. Het doelsaldo\n\n    3. Het meest gescoorde aantal doelpunten\n\n    4. Het onderling resultaat (indien er tegen elkaar is gespeeld)\n\n    5. Strafworpen\n\n7. Strafworpen als genoemd in 6.5 vinden bij de wedstrijdleiding plaats\n\n8. Protesten tegen beslissingen van de scheidsrechters worden niet aanvaard\n\n9. Indien beide ploegen een tenue van gelijke kleur hebben dan dient de uitspelende (de tweede-genoemde ploeg) zorg te dragen voor reserveshirts\n\n10. In alle gevallen waarin dit reglement niet voorziet beslist de wedstrijdleiding")

if choose == "Turf War":
    import leafmap.foliumap as leafmap

    st.markdown('Under construction')
    password = st.text_input("Enter password", type="password")
    if not password == "ffwachten":
        st.stop()
    else:

        if not cookies.ready():
            # Wait for the component to load and send us current cookies.
            st.stop()

        lat_location = False
        lon_location = False
        result = False

        st.markdown(""" <style> .font {
        font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
        </style> """, unsafe_allow_html=True)
        if 'club' in cookies:
            title = 'Turf War - ' + cookies['club']
        else:
            title = 'Turf War'
        st.markdown(f'<p class="font">{title}</p>', unsafe_allow_html=True)

       #st.write("Current cookies:", cookies)

        if not 'club' in cookies:
            teams = sorted(
                [i for i in np.unique(schema[['Thuis', 'Uit']]) if not i.startswith('No ') and not i.startswith('No.')])
            verenigingen = sorted(set([j[0] if (j := i.split(' ')) and len(str(j[-1])) <= 2 else i for i in teams]))

            option = st.selectbox('Kies je club:', ['']+verenigingen,
                                    format_func=lambda x: 'Kies een club' if x == '' else x)

            if option:

                st.warning(f'Je hebt {option} geselecteerd. Bevestig je keuze of kies een andere club. Je kunt je club tijdens het spel niet meer wijzigen.')

                if st.button("Bevestig"):
                    with st.spinner(f"Registreren voor {option}"):
                        cookies['club'] = option  # This will get saved on next rerun
                        cookies.save()  # Force saving the cookies now, without a rerun
                        st.success(f'Je speelt mee namens {option}')
                        st.experimental_rerun()

        if 'club' in cookies:
            loc_button = Button(label="Get Device Location", max_width=150)
            loc_button.js_on_event(
                "button_click",
                CustomJS(
                    code="""
                navigator.geolocation.getCurrentPosition(
                    (loc) => {
                        document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
                    }
                )
                """
                ),
            )
            result = streamlit_bokeh_events(
                loc_button,
                events="GET_LOCATION",
                key="get_location",
                refresh_on_update=False,
                override_height=75,
                debounce_time=0,
            )

        file_path = 'Hemelvaart_De_Sprong.geojson'
        gdf = gpd.read_file(file_path)

        #test
        result= {'GET_LOCATION': True,'lat': 51.497130, 'lon': 3.593360}
        if result:
            if "GET_LOCATION" in result:
                #loc = result.get("GET_LOCATION")
                #lat_location = float(loc.get("lat"))
                #lon_location = float(loc.get("lon"))
                lat_location = float(result["lat"])
                lon_location = float(result["lon"])
                #filter gdf on geometries that contain the location Point
                hits = gdf[gdf['geometry'].contains(Point(lon_location, lat_location))].iloc[0]
                if len(hits) > 0:
                    st.success(f"Lat, Lon: {lat_location}, {lon_location}")

        lon, lat = leafmap.gdf_centroid(gdf)

        m = leafmap.Map(center=(lat, lon), draw_export=False, draw_control=False, measure_control=False,
                        fullscreen_control=False, attribution_control=True)
        m.add_gdf(gdf, layer_name='Turf Wars Hemelvaart')
        if lat_location and lon_location:
            m.add_marker(location=(lat_location, lon_location))
        m.zoom_to_gdf(gdf)
        m.to_streamlit(add_layer_control=True)
