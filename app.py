import geopandas as gpd
import leafmap.foliumap as leafmap
import numpy as np
import pandas as pd
import pygsheets
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from google.oauth2 import service_account
from shapely.geometry import Point
from streamlit_bokeh_events import streamlit_bokeh_events
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_option_menu import option_menu
from zoneinfo import ZoneInfo

# VARS
timezone_str = "Europe/Amsterdam"
timezone = ZoneInfo(timezone_str)
start_time = '2022-05-01 14:15'
end_time = '2022-05-26 16:00'
start_time_turfwar = pd.to_datetime(start_time).tz_localize(tz=timezone_str)
end_time_turfwar = pd.to_datetime(end_time).tz_localize(tz=timezone_str)

# CONFIG
st.set_page_config(page_title='Swift Hemelvaartsdagtoernooi', page_icon="favicon.ico", layout="wide")
# This should be on top of your script
cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="rjadr/streamlit-cookies-manager/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=st.secrets["cookie_password"]
)

hide_st_style = """
            <link href="https://fonts.cdnfonts.com/css/cooper-black" rel="stylesheet">
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .font {
font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# FUNCTIONS
@st.cache(ttl=300)  # 5 minute cache
def get_stand(sheet_nr):
    url_stand = f'https://docs.google.com/spreadsheets/d/{sheet_nr}/gviz/tq?tqx=out:csv&sheet=Standen'
    stand_df = pd.read_csv(url_stand, skiprows=1, usecols=[0, 1, 2, 3, 4, 5, 6, 7],
                           names=['Poule', 'Team', 'Voor', 'Tegen', 'Doelsaldo', 'Gespeeld', 'Punten', 'Stand'])
    return stand_df


@st.cache(ttl=300)  # 5 minute cache
def get_schema(sheet_nr):
    url_schema = f'https://docs.google.com/spreadsheets/d/{sheet_nr}/gviz/tq?tqx=out:csv&sheet=Speelschema'
    schema_df = pd.read_csv(url_schema, usecols=list(range(0, 10)))
    schema_df['Score uit'] = schema_df['Score uit'].astype('Int64')
    schema_df['Score thuis'] = schema_df['Score thuis'].astype('Int64')
    return schema_df


# @st.cache(ttl=150)
def get_turfwar_stand(status, sheet_nr):
    url_schema = f'https://docs.google.com/spreadsheets/d/{sheet_nr}/gviz/tq?tqx=out:csv&sheet=TurfWar'
    turfwar = pd.read_csv(url_schema, usecols=list(range(0, 3)))
    turfwar['start_time'] = pd.to_datetime(turfwar['start_time']).dt.tz_localize(tz=timezone_str)
    if turfwar.empty:
        return None
    else:
        end_time = end_time_turfwar if status == "closed" else pd.Timestamp.now(timezone)

        turfwar['tijd totaal'] = pd.to_timedelta(
            turfwar.groupby('h3')['start_time'].diff(periods=-1).dt.total_seconds().abs().fillna(
                (turfwar['start_time'] - end_time).dt.total_seconds().abs()), unit='S')

        stand_df = turfwar.groupby('club').agg({'h3': ['nunique'], 'tijd totaal': ['sum']}).reset_index().droplevel(1,
                                                                                                                    axis=1).rename(
            columns={'h3': 'aantal gebieden'}).sort_values(by=['tijd totaal', 'aantal gebieden'],
                                                           ascending=False).reset_index(drop=True)
        stand_df['tijd totaal'] = stand_df['tijd totaal'].apply(lambda
                                                                    td: f'{(td.components.days * 24) + td.components.hours} uur, {td.components.minutes} minuten, {td.components.minutes} seconden')
        stand_df.index = stand_df.index + 1
        return stand_df


def get_turfwar_bezetting(sheet_nr):
    url_schema = f'https://docs.google.com/spreadsheets/d/{sheet_nr}/gviz/tq?tqx=out:csv&sheet=TurfWarBezetting'
    turfwar = pd.read_csv(url_schema)
    turfwar['start_time'] = pd.to_datetime(turfwar['start_time']).dt.tz_localize(tz=timezone_str)
    return turfwar

@st.cache()
def initialize_pygsheets(sheet='TurfWar'):
    credentials_obj = service_account.Credentials.from_service_account_info(
        get_gsheet_credentials(),
        scopes=('https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'))
    gc = pygsheets.authorize(custom_credentials=credentials_obj)
    sh = gc.open(sheet)
    return sh


def write_turnwar(h3, club):
    sh = initialize_pygsheets('TurfWar')
    wks = sh[0]  # select the first sheet
    wks.append_table(values=[pd.Timestamp.now(timezone).strftime('%Y-%m-%d %H:%M:%S.%f'), h3, club])  # append row to worksheet .strftime('%d-%m-%Y %H:%M:%S')


def get_turfwar_sheet():
    sh = initialize_pygsheets('TurfWar')
    wks = sh[0]  # select the first sheet
    return wks.get_as_df()


@st.cache
def get_programma():
    table = {
        "Tijd": {
            0: "10:00",
            1: "10:30",
            2: "11:00",
            3: "11:30",
            4: "12:00",
            5: "12:30",
            6: "13:00",
            7: "13:30",
            8: "14:00",
            9: "14:30",
            10: "15:00",
            11: "15:30",
            12: "16:10",
        },
        "Kinderprogramma (Kangoeroes, F, E, D)": {
            0: "Opening toernooi met warming up op hoofdveld Swift",
            1: "Schminken, Tekenen, Springkussen",
            2: "Schminken, Tekenen, Springkussen",
            3: "Schminken, Tekenen, Springkussen",
            4: "Springkussen",
            5: "Springkussen",
            6: "Spelletjesparcours, Springkussen",
            7: "Spelletjesparcours, Springkussen",
            8: "Spelletjesparcours, Springkussen",
            9: "Spelletjesparcours, Springkussen",
            10: "Springkussen",
            11: "Springkussen",
            12: " ",
        },
        "Toernooi": {
            0: "Opening toernooi met warming up op hoofdveld Swift",
            1: "Ronde 1",
            2: "Ronde 2",
            3: "Ronde 3",
            4: "Ronde 4",
            5: "Ronde 5",
            6: "Ronde 6",
            7: "Ronde 7",
            8: "Ronde 8",
            9: "Ronde 9",
            10: "Ronde 10",
            11: "Ronde 11",
            12: "Prijsuitreiking",
        },
    }
    return pd.DataFrame(table)


@st.cache(allow_output_mutation=True)
def get_map():
    file_path = 'Hemelvaart_De_Sprong.geojson'
    return gpd.read_file(file_path)


@st.cache(allow_output_mutation=True)
def get_logo():
    return Image.open('swiftlogo.png')


@st.cache(allow_output_mutation=True)
def get_plattegrond():
    return Image.open('plattegrond_hemelvaart.jpg')


color_mapping = {'A1 Reunited': '#FFC0CB',
                 'Albatros': '#FFFFFF',
                 'Appels': '#c0ffc3',
                 'BKC': '#A62D00',
                 'Fortis': '#FFFF00',
                 'Luctor': '#fed8b1',  # licht oranje
                 'Mand': '#C8E71D',
                 'Ondo': '#0000FF',
                 'Seolto': '#ADD8E6',  # lichtblauw
                 'Stormvogels': '#000000',
                 'Swift': '#FF9900',
                 'Team Gillissen': '#35D3BF',
                 'Temse': '#601de7',
                 'Tjoba': '#008000',
                 'Togo': '#FF0000',  # rood/wit
                 'Top': '#FFDFDF',  # wit/rood
                 'Volharding': '#bd9f9f',  # rood/wit
                 }


def fill_color(feat):
    if feat['properties']['club']:
        fillcolor = color_mapping[feat['properties']['club']]
        fillopacity = 0.5
    else:
        fillcolor = '#000000'
        fillopacity = 0.0
    return {'color': '#000000', 'fillColor': fillcolor, "weight": 0.5, "fillOpacity": fillopacity}


@st.cache(allow_output_mutation=True)
def get_color_table():
    # create html table
    table = '<table style="width:100%">'
    # create header row
    table += '<tr>'
    table += '<th>Club</th>'
    table += '<th>Kleur</th>'
    table += '</tr>'
    # create rows with team name and color
    for team, color in color_mapping.items():
        table += '<tr>'
        table += '<td>' + team + '</td>'
        table += f'<td><span style="height: 25px; width: 25px; background-color:' + color + '; border: 1px solid black; border-radius: 50%; display: inline-block;"></span></td>'
        table += '</tr>'
    # close table
    table += '</table>'
    return table


def get_gsheet_credentials():
    return {
        "type": st.secrets["gsheets_type"],
        "project_id": st.secrets["gsheets_project_id"],
        "private_key_id": st.secrets["gsheets_private_key_id"],
        "private_key": st.secrets["gsheets_private_key"],
        "client_email": st.secrets["gsheets_client_email"],
        "client_id": st.secrets["gsheets_client_id"],
        "auth_uri": st.secrets["gsheets_auth_uri"],
        "token_uri": st.secrets["gsheets_token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gsheets_auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gsheets_client_x509_cert_url"]
    }


# APP CONTENTS
with st.sidebar:
    choose = option_menu("kv Swift Hemelvaartsdagtoernooi",
                         ["Welkom", "Toernooi-informatie", "Wedstrijdschema", "Standen", "Plattegrond",
                          "Wedstrijdreglement", "Turf War"],
                         icons=['house', 'info-circle', 'calendar3', 'trophy', 'map', 'journal-check', 'flag'],
                         menu_icon="app-indicator", default_index=0,
                         styles={
                             "container": {"padding": "5!important", "background-color": "#fafafa"},
                             "icon": {"color": "black", "font-size": "25px"},
                             "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                                          "--hover-color": "#eee"},
                             "nav-link-selected": {"background-color": "#FF9900"},
                         }, orientation="vertical",
                         )

if choose == "Welkom":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:  # To display the header text using css style
        st.markdown('<p class="font">Welkom!</p>', unsafe_allow_html=True)
    with col2:  # To display brand log
        st.image(get_logo(), width=130)

    st.warning("Let op: wedstrijden van TOGO 2 (poule Sb) en Top A (poule Ab) zijn komen te vervallen. Het wedstrijdrooster is actueel.")
    st.markdown(
        "Het is weer zo ver, voor de 72e keer in de geschiedenis van Swift vindt het kv Swift Hemelvaartsdagtoernooi plaats! Op het moment van het schrijven van dit voorwoord hebben 14 verenigingen en 92 teams aangemeld. Heel erg fijn dat zoveel sporters naar Swift komen om te genieten van dit jaarlijkse toernooi!\n\nOp deze site vindt u alle informatie over het toernooi. U kunt o.a. het wedstrijdschema, de standen, de plattegrond en het wedstrijdreglement bekijken. Browst u mobiel? Klik dan op de pijl linksboven om het menu te zien.\n\nWe wensen u een mooi toernooi toe!\n\nVriendelijke groet,\n\nDe toernooicommissie van het kv Swift Hemelvaartsdagtoernooi")

elif choose == "Toernooi-informatie":
    st.markdown('<p class="font">Toernooi-informatie</p>', unsafe_allow_html=True)

    st.markdown("Hieronder vindt u praktische informatie over de toernooidag:\n\n### Programma")

    st.table(get_programma())
    st.markdown(
        "### Parkeren\n\nParkeren met de auto is mogelijk op het parkeerterrein van Sportpark de Sprong. Fietsers verzoeken wij de fiets te parkeren in de fietsenrekken voor de ingang van de sporthal en niet bij (de toegangsweg naar) het clubhuis.\nDe toegangsweg naar het complex is niet voor autoverkeer toegankelijk en dient vrij gehouden te worden voor de hulpdiensten.\n\n### Aankomst/melden\n\nWij verzoeken teams dringend op tijd aanwezig te zijn en zich uiterlijk om 10:00 uur te melden bij de wedstrijdleiding (bij het materialenhok naast het clubhuis, zie plattegrond). We wijzen erop dat het niet mogelijk is een wedstrijd op een later tijdstip te spelen. Zie punt 4 van het wedstrijdreglement.\n\nDe terreinen zijn toegankelijk vanaf 9 uur 's morgens.\n\n### Kinderactiviteiten\n\nNaast de wedstrijden dit jaar extra activiteiten voor de jeugd. Het toernooi zal geopend worden met een muzikale warming-up waarbij iedereen zich klaar kan maken voor een sportieve dag. Alle spelende en niet-spelende jeugd kan meedoen, maar ook senioren die een extra warming-up nodig hebben zijn meer dan welkom om aan te sluiten. Verder kun je je dit jaar laten schminken en een sprongetje wagen op het springkussen. In de middag vinden er spelletjes plaats voor de jonge jeugd. Voltooi alle spellen en krijg een kleine beloning! Neem je broertjes, zusjes, vriendjes en vriendinnetjes mee om samen tussen de wedstrijden door te spelen.\n\nKinderen kunnen vrijblijvend aansluiten bij de activiteiten buiten het wedstrijdprogramma om.\n\nHiernaast is het spel Turf War te spelen via [https://hemelvaart.kvswift.nl](https://hemelvaart.kvswift.nl). Wie verovert Sportpark de Sprong namens zijn club? Check met je mobiel in op zoveel mogelijk locaties op het sportpark. De club die het langst zoveel mogelijk locaties in bezit houdt wint de Turf War!\n\n### Afval\n\nVoor afval treft u zowel bij de kleedruimten, kantine als op het veld speciale afvalbakken aan. Men wordt dringend verzorgd deze te gebruiken!\n\n### EHBO\n\nDe EHBO-post bevindt zich bij de kleedkamers naast het clubhuis.\n\n### Prijzen\n\nVoor elke afdeling is één prijs beschikbaar. De prijsuitreiking vindt plaats om 16:10 uur bij het kunstgrasveld voor het clubhuis. Voor de D,E en F-jeugd is er voor ieder kind een vaantje beschikbaar, deze kunnen vanaf 12.00 uur door de coaches opgehaald worden bij de wedstrijdleiding.\n\n### (Kunst)grasvelden\n\nVelden S4 (senioren), E1, E2, E3, F1 en F2 zijn gelegen op de kunstgrasvelden. Alle andere velden op natuurgras. Zie het wedstrijdschema om te kijken op welke velden je speelt.\n\n### Fluiten\n\nNa aankomst ontvangt u de wedstrijdbriefjes met de te fluiten wedstrijden. Wilt u de uitslagen z.s.m. na afloop van de wedstrijd doorgeven bij de wedstrijdleiding? De scheidsrechters geven de bal door aan de volgende scheidsrechter, tenzij op het briefje verzocht wordt de bal bij de leiding in te leveren.\n\n### Overig\n\nK.v. Swift stelt zich niet aansprakelijk voor het zoekraken of beschadigen van eigendommen. Het is de deelnemende verenigingen niet toegestaan tijdens het toernooi verkoopacties te houden op de velden.\n\n### Eten en drinken\n\nEten en drinken wordt afgerekend met consumptiebonnen die in het clubhuis te verkrijgen zijn. 's Middags zijn ze ook te koop bij het snoep/ijs.\n\n### Locatie en contact\n\nKorfbalvereniging Swift\n\nSportcomplex de Sprong\n\nDe Aanloop 5\n\n4335 AT Middelburg\n\nTel. 0118 850 437 (clubhuis)\n\ne-mail: [kvswifthemelvaart@gmail.com](mailto:kvswifthemelvaart@gmail.com)")
    st.map(data=pd.DataFrame([{'lat': 51.497489353450895, 'lon': 3.594653606414795}]))

elif choose == "Wedstrijdschema":
    schema = get_schema(st.secrets["stand_sheetid"])
    scheidsrechters = sorted(list(schema['Scheidsrechter'].drop_duplicates()))
    teams = sorted(
        [i for i in np.unique(schema[['Thuis', 'Uit']]) if not i.startswith('No ') and not i.startswith('No.')])
    verenigingen = sorted(set([j[0] if (j := i.split(' ')) and len(str(j[-1])) <= 2 else i for i in teams]))
    poules = sorted(list(schema['Poule'].drop_duplicates()))
    rondes = sorted(list(schema['Ronde'].drop_duplicates()))

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
            cross_finals_filter = (schema['Poule'].str.contains('|'.join(poule_nrs), na=False)) & (
                    schema['Thuis'].str.startswith('No ') | schema['Thuis'].str.startswith('No.'))
            teams_filter = schema[['Thuis', 'Uit']].isin(filter_value).any(axis=1)
            return np.logical_or(teams_filter, cross_finals_filter)
        elif filter_name == 'verenigingen_choice':
            poule_nrs = schema[(schema['Thuis'] + ' ' + schema['Uit']).str.contains('|'.join(filter_value))][
                'Poule'].unique()
            cross_finals_filter = (schema['Poule'].str.contains('|'.join(poule_nrs), na=False)) & (
                    schema['Thuis'].str.startswith('No ') | schema['Thuis'].str.startswith('No.'))
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


    # filter non empty items in filters
    filters = [filter_df(k, v) for k, v in filters.items() if v]
    filter_ = np.full(len(schema), True)
    filter_ = np.logical_and.reduce((filter_, *filters))

    df_schema = schema.copy()
    st.dataframe(df_schema[filter_].sort_values(["Ronde", "Poule"],
                                                ascending=True).reset_index(drop=True))

elif choose == "Standen":
    st.markdown('<p class="font">Standen</p>', unsafe_allow_html=True)

    #  st.markdown('Kies poule of team om de standen te zien')
    stand = get_stand(st.secrets["stand_sheetid"])
    # remove item from pandas series if startswith 'No ' or 'No.'
    teams = [i for i in stand['Team'].drop_duplicates().sort_values().to_list() if
             not i.startswith('No ') and not i.startswith('No.')]

    team = st.selectbox('Kies je team:', [''] + teams,
                                          format_func=lambda x: 'Kies een team' if x == '' else x)
    
    if team:
        filter_ = stand['Poule'].eq(stand[stand['Team'] == team]['Poule'].values[0])
        df_stand = stand.copy()
        df_stand = df_stand[filter_].sort_values(["Stand"],
                                                 ascending=True).reset_index(drop=True)
        df_stand.index = range(1, df_stand.shape[0] + 1)
        st.dataframe(df_stand[['Team', 'Voor', 'Tegen', 'Doelsaldo', 'Gespeeld', 'Punten']])

elif choose == "Plattegrond":
    st.markdown('<p class="font">Plattegrond</p>', unsafe_allow_html=True)
    st.image(get_plattegrond(), use_column_width=True)

elif choose == "Wedstrijdreglement":
    st.markdown('<p class="font">Wedstrijdreglement</p>', unsafe_allow_html=True)
    st.markdown(
        "1. De wedstrijden worden gespeeld volgens de regels van de KNKV\n\n2. Elke wedstrijd duurt 25 (2x 12 1⁄2 ) minuten. Zowel het begin -, het rust- als het eindsignaal worden centraal gegeven. Bij pupillen (D,E & F) wordt er in de rust van functie (én niet van vak) gewisseld, ongeacht het aantal doelpunten. De E- en F-jeugd neemt eerst ieder 3 strafworpen, spelen tot het wissel- (bel)signaal, beginnen weer met ieder 3 strafworpen en spelen dan de wedstrijd uit. De strafworpen worden niet meegeteld voor de einduitslag. Na iedere ronde is er 5 minuten om te wisselen en op te stellen.\n\n3. De eerstgenoemde ploeg in het programma heeft de vakkeuze en neemt de bal uit\n\n4. Een team dat bij de rust nog niet gereed is wordt geacht niet te zijn opgekomen. De uitslag wordt dan 3-0 in het voordeel van de tegenpartij.\n\n5. In afdelingen van vier ploegen wordt de stand opgemaakt na een halve competitie en volgt daarna de finale-wedstrijd en de strijd om de 3e plaats. De winnaar van de finale-wedstrijd is kampioen in de afdeling. Bij een gelijkspel in een finale-wedstrijd telt regel 6 (zie hieronder) In afdelingen van 5 of 6 teams wordt géén finale gespeeld.\n\n6. De plaatsing van de ploegen in de eindrangschikking wordt bepaald door:\n\n    1. Het aantal wedstrijdpunten\n\n    2. Het doelsaldo\n\n    3. Het meest gescoorde aantal doelpunten\n\n    4. Het onderling resultaat (indien er tegen elkaar is gespeeld)\n\n    5. Strafworpen\n\n7. Strafworpen als genoemd in 6.5 vinden bij de wedstrijdleiding plaats\n\n8. Protesten tegen beslissingen van de scheidsrechters worden niet aanvaard\n\n9. Indien beide ploegen een tenue van gelijke kleur hebben dan dient de uitspelende (de tweede-genoemde ploeg) zorg te dragen voor reserveshirts\n\n10. In alle gevallen waarin dit reglement niet voorziet beslist de wedstrijdleiding")

elif choose == "Turf War":
  #  if 'pwcheck' not in st.session_state:
  #      st.warning('Under construction')
  #      password = st.text_input("Enter password", type="password")
  #      if password == st.secrets["pw_under_construction"]:
  #          st.success('Correct')
  #          st.session_state['pwcheck'] = True
  #          st.experimental_rerun()
  #  else:
        choose2 = option_menu(None, ["Spel", "Stand", "Help"],
                              icons=['puzzle', 'trophy', "question-circle"],
                              menu_icon="cast", default_index=0, orientation="horizontal")

        if choose2 == "Spel":
            if (pd.Timestamp.now(timezone) > start_time_turfwar) and (
                    pd.Timestamp.now(timezone) < end_time_turfwar):
                if not cookies.ready():
                    # Wait for the component to load and send us current cookies.
                    st.stop()

                if 'club' not in cookies:
                    verenigingen = list(color_mapping.keys())
                    option = st.selectbox('Kies je club:', [''] + verenigingen,
                                          format_func=lambda x: 'Kies een club' if x == '' else x)

                    if option:
                        st.warning(
                            f'Je hebt {option} geselecteerd. Bevestig je keuze of kies een andere club. Je kunt je club tijdens het spel niet meer wijzigen.')
                        if st.button("Bevestig"):
                            with st.spinner(f"Registreren voor {option}"):
                                cookies['club'] = option  # This will get saved on next rerun
                                cookies.save()  # Force saving the cookies now, without a rerun
                                st.success(f'Je speelt mee namens {option}')
                                st.experimental_rerun()

                elif 'club' in cookies:
                    gdf = get_map()
                    #df = get_turfwar_bezetting(st.secrets["turfwar_sheetid"])
                    df = get_turfwar_sheet()

                    lat_location = False
                    lon_location = False

                    loc_button = Button(label="verover gebied", button_type="primary")
                    loc_button.js_on_event("button_click", CustomJS(code="""
                        if (!navigator.geolocation) {
                            document.dispatchEvent(new CustomEvent("GET_LOCATION", {
                                detail: {
                                    error: "Geolocatie wordt niet ondersteund door deze browser."
                                }
                            }));
                        } else {
                            navigator.geolocation.getCurrentPosition(
                                (loc) => {
                                    document.dispatchEvent(new CustomEvent("GET_LOCATION", {
                                        detail: {
                                            lat: loc.coords.latitude,
                                            lon: loc.coords.longitude
                                        }
                                    }))
                                },
                                (err) => {
                                    document.dispatchEvent(new CustomEvent("GET_LOCATION", {
                                        detail: {
                                            error: err.message
                                        }
                                    }))
                                }, {
                                    enableHighAccuracy: true,
                                    timeout: 5000,
                                    maximumAge: 0
                                }
                            )
                        }
                        """))
                    result = streamlit_bokeh_events(
                        loc_button,
                        events="GET_LOCATION",
                        key="get_location",
                        refresh_on_update=False,
                        override_height=75,
                        debounce_time=0)

                    ##############TESTING#############
                    # result = {'GET_LOCATION': True, 'lat': 51.497130, 'lon': 3.593360}
                    ##################################

                    if result:
                        if "GET_LOCATION" in result:
                            if "error" in result["GET_LOCATION"]:
                                st.error(result["GET_LOCATION"]["error"])
                            elif "lat" in result["GET_LOCATION"] and "lon" in result["GET_LOCATION"]:
                                loc = result.get("GET_LOCATION")
                                lat_location = float(loc.get("lat"))
                                lon_location = float(loc.get("lon"))

                                ########TESTING############
                                #  st.write(result.get("GET_LOCATION"))
                                #   lat_location = float(result["lat"])
                                #   lon_location = float(result["lon"])
                                ###########################

                                # filter gdf on geometries that contain the location Point
                                hits = gdf[gdf['geometry'].contains(Point(lon_location, lat_location))]

                                if not hits.empty:
                                    hit = hits.iloc[0]
                                    #st.success(f"Lat, Lon: {lat_location}, {lon_location}")
                                    # check with current map
                                    claim_exists = df[df['h3'] == hit['h3']]
                                    st.dataframe(claim_exists)
                                    st.write(hit['h3'])
                                    st.dataframe(df)

                                    if not claim_exists.empty:
                                        claim = claim_exists.iloc[0]
                                        if claim['club'] == cookies['club']:
                                            st.warning('Je hebt deze locatie al geclaimd.')
                                        elif (remaining_time := (pd.Timestamp.now(timezone) - claim['start_time']).seconds) < 120:
                                            st.warning(
                                                f"Deze locatie is zojuist door een andere club al geclaimd. Wacht nog {int(remaining_time)} seconden.")
                                        else:
                                            st.success('Je hebt deze locatie succesvol geclaimd.')
                                            write_turnwar(hit['h3'], cookies['club'])
                                            df[df['h3'] == hit['h3']]['club'] = cookies['club']
                                    else:
                                        st.success('Je hebt deze locatie succesvol geclaimd.')
                                        write_turnwar(hit['h3'], cookies['club'])
                                        df.loc[len(df)] = [None, hit['h3'], cookies['club']]
                                else:
                                    st.warning('Je locatie ligt buiten het speelveld.')
                        else:
                            st.warning('Je locatie is niet goed doorgekomen.')

                    gdf = gdf.merge(df, on='h3', how='outer')

                    m = leafmap.Map(draw_export=False, draw_control=False, measure_control=False,
                                    fullscreen_control=False, attribution_control=True)

                    m.add_gdf(gdf[['club', 'h3', 'geometry']], layer_name='Turf War Hemelvaart',
                              style_function=fill_color)
                    if lat_location and lon_location:
                        m.add_marker(location=(lat_location, lon_location))
                    m.zoom_to_gdf(gdf)
                    # m.add_legend(title="Clubs", legend_dict=color_mapping)
                    m.to_streamlit(add_layer_control=True)
                    st.markdown('### Legenda')
                    st.markdown(get_color_table(), unsafe_allow_html=True)
            elif pd.Timestamp.now(timezone) < start_time_turfwar:
                st.warning(f'Het spel begint pas op {start_time}.')
            elif pd.Timestamp.now(timezone) > end_time_turfwar:
                st.warning(f'Het spel is afgelopen op {end_time}. Bekijk de stand!')
            else:
                st.warning('Het spel is niet actief.')
        elif choose2 == "Stand":
            if (pd.Timestamp.now(timezone) > start_time_turfwar) and (
                    pd.Timestamp.now(timezone) < end_time_turfwar):
                if (stand := get_turfwar_stand('open', st.secrets["turfwar_sheetid"])) is not None:
                    st.dataframe(stand)
                else:
                    st.warning('Er is geen stand beschikbaar.')
            elif pd.Timestamp.now(timezone) < start_time_turfwar:
                st.warning(f'Het spel begint pas op {start_time}.')
            elif pd.Timestamp.now(timezone) > end_time_turfwar:
                if (stand := get_turfwar_stand('closed', st.secrets["turfwar_sheetid"])) is not None:
                    st.success(
                        f'Gefeliciteerd **{stand.iloc[0]["club"]}**, winnaars van de kv Swift Turf War! Eeuwige roem valt jullie ten deel!')
                    st.dataframe(stand)
                    st.balloons()
                else:
                    st.warning('Er is geen stand beschikbaar.')
            else:
                st.warning('Het spel is niet actief.')
        elif choose2 == "Help":
            st.markdown(
                "### Spelregels\n\nHet speelveld is opgeldeeld in vakken. Je kunt een vak voor je club 'veroveren' door naar het vak toe te lopen en ter plekke op de knop 'verover gebied' te drukken. Als je je in dit gebied bevindt zal het veld op de kaart in de kleur van je club kleuren. Verover zoveel mogelijk gebieden, want de club die de langste tijd de meeste gebieden in bezit heeft gehad wint!\n\nHet spel start op Hemelvaartsdag om 09:00 uur en duurt tot 16:00 uur. De definitieve winnaar is dan bekend onder Stand.\n\nDenk strategisch na over welke gebieden je wilt veroveren en vergeet niet je tegenstanders te dwarsbomen door hun gebieden te veroveren.\n\nZorg dat de browser op je mobiel je locatie deelt in de browser en zet je GPS aan, anders kun je geen gebieden veroveren.")

# https://github.com/streamlit/streamlit/issues/1291
# auto-close menu on click
components.html("""
<script type="text/javascript">
const doc = window.parent.document.querySelector('[title="streamlit_option_menu.option_menu"]');
const links = doc.contentWindow.document.querySelectorAll(".nav-link");
const buttons = window.parent.document.querySelector('section[data-testid="stSidebar"]').getElementsByTagName('button');
for (const link of links) {
    link.addEventListener('click', function() {
    buttons[0].click();
    return false;
  });
}
</script>
""", height=0, width=0)
