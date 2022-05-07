import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from PIL import Image

st.set_page_config(page_title='Swift Hemelvaartsdagtoernooi', page_icon="favicon.ico", layout="wide")
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown('<link href="http://fonts.cdnfonts.com/css/cooper-black" rel="stylesheet">', unsafe_allow_html = True)

with st.sidebar:
    choose = option_menu("kv Swift Hemelvaartsdagtoernooi", ["Welkom", "Toernooi-informatie", "Wedstrijdschema", "Standen", "Plattegrond", "Wedstrijdreglement"],
                         icons=['house', 'info-circle', 'calendar3', 'trophy', 'map', 'journal-check'],
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

### if knockout in poule ook knockout laten zien

logoswift = Image.open('swiftlogo.png')
logojumbo = Image.open('jumbologo.jpg')
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

    st.markdown("Het is weer zo ver, voor de 72e keer in de geschiedenis van Swift vindt het Jumbo-Swift Hemelvaartsdagtoernooi plaats! Op het moment van het schrijven van dit voorwoord hebben 14 verenigingen en 92 teams aangemeld. Heel erg fijn dat zoveel sporters naar Swift komen om te genieten van dit jaarlijkse toernooi!\n\nHet toernooi wordt mede mogelijk gemaakt door onze sponsor [Jumbo Oostkapelle/Middelburg](https://www.jumbo.com/).\n\n")

    col1, col2, col3 = st.columns([1.4, 3, 1.4])
    col2.image(logojumbo, use_column_width=True)

    st.markdown("Op deze site vindt u alle informatie over het toernooi. U kunt o.a. het wedstrijdschema, de standen, de plattegrond en het wedstrijdreglement bekijken. Browst u mobiel? Klik dan op de pijl linksboven om het menu te zien.\n\nWe wensen u een mooi toernooi toe!\n\nVriendelijke groet,\n\nDe toernooicommissie van het Jumbo-Swift Hemelvaartsdagtoernooi")

if choose == "Toernooi-informatie":
    st.markdown(""" <style> .font {
    font-size:35px ; font-family: 'Cooper Black'; color: #FF9900;} 
    </style> """, unsafe_allow_html=True)
    st.markdown('<p class="font">Toernooi-informatie</p>', unsafe_allow_html=True)

    st.markdown("Hieronder vindt u praktische informatie over de toernooidag:\n\n### Parkeren\n\nParkeren met de auto is mogelijk op het parkeerterrein van Sportpark de Sprong. Fietsers verzoeken wij de fiets te parkeren in de fietsenrekken voor de ingang van de sporthal en niet bij (de toegangsweg naar) het clubhuis.\nDe toegangsweg naar het complex is niet voor autoverkeer toegankelijk en dient vrij gehouden te worden voor de hulpdiensten.\n\n### Aankomst/melden\n\nWij verzoeken teams dringend op tijd aanwezig te zijn en zich uiterlijk om 10:00 uur te melden bij de wedstrijdleiding (bij het materialenhok naast het clubhuis, zie plattegrond). We wijzen erop dat het niet mogelijk is een wedstrijd op een later tijdstip te spelen. Zie punt 4 van het wedstrijdreglement.\n\nDe terreinen zijn toegankelijk vanaf 9 uur 's morgens.\n\n### Warming up\n\n....\n\n### Kinderactiviteiten\n\n....\n\n### Afval\n\nVoor afval treft u zowel bij de kleedruimten, kantine als op het veld speciale afvalbakken aan. Men wordt dringend verzorgd deze te gebruiken!\n\n### EHBO\n\nDe EHBO-post bevindt zich bij de kleedkamers naast het clubhuis.\n\n### Prijzen\n\nVoor elke afdeling is één prijs beschikbaar. De prijsuitreiking vindt plaats om ??? uur bij ???. Voor de D,E en F-jeugd is er voor ieder kind een vaantje beschikbaar, deze kunnen vanaf 12.00 uur door de coaches opgehaald worden bij de wedstrijdleiding.\n\n### (Kunst)grasvelden\n\nVelden S4 (senioren), E1, E2, E3, F1 en F2 zijn gelegen op de kunstgrasvelden. Alle andere velden op natuurgras. Zie het wedstrijdschema om te kijken op welke velden je speelt.\n\n### Fluiten\n\nNa aankomst ontvangt u de wedstrijdbriefjes met de te fluiten wedstrijden. Wilt u de uitslagen z.s.m. na afloop van de wedstrijd doorgeven bij de wedstrijdleiding? De scheidsrechters geven de bal door aan de volgende scheidsrechter, tenzij op het briefje verzocht wordt de bal bij de leiding in te leveren.\n\n### Overig\n\nK.v. Swift stelt zich niet aansprakelijk voor het zoekraken of beschadigen van eigendommen. Het is de deelnemende verenigingen niet toegestaan tijdens het toernooi verkoopacties te houden op de velden.\n\n###Eten en drinken\n\nEten en drinken wordt afgerekend met consumptiebonnen die op verschillende punten te verkrijgen zijn.\n\n### Locatie en contact\n\nKorfbalvereniging Swift\n\nSportcomplex de Sprong\n\nDe Aanloop 5\n\n4335 AT Middelburg\n\nTel. 0118 850 437 (clubhuis)\n\ne-mail: [kvswifthemelvaart@gmail.com](mailto:kvswifthemelvaart@gmail.com)")
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