# -*- coding: utf-8 -*-
from .chart import Chart
from . import database as datab
from .extensions.path import path

ccodes = {
'AF': 'AFG'	,	#Afganistán
'AM': 'ARM'	,	#Armenia
'AJ': 'ASB'	,	#Azerbaiján
'BA': 'BRN'	,	#Bahrain
'BG': 'BD'    ,	#Bangla Desh
'BT': 'BHU'	,	#Bhután
'BX': 'BRU'	,	#Brunei
'CB': 'K'     ,	#Camboya
'CH': 'TJ'    ,	#China
'CY': 'CY'    ,	#Chipre
'GG': 'GRG'	,	#Georgia
'HK': 'HKG'	,	#Hong Kong
'IN': 'IND'	,	#India
'ID': 'RI'    ,	#Indonesia
'IR': 'IR'    ,	#Irán
'IZ': 'IRQ'	,	#Irak
'IS': 'IL'    ,	#Israel
'JA': 'J'     ,	#Japón
'JO': 'JOR'	,	#Jordania
'KZ': 'KAZ'	,	#Kazajstán
'KN': 'KOR'	,	#Corea del Norte
'KS': 'ROK'	,	#Corea del Sur
'KU': 'KWT'	,	#Kuwait
'KG': 'KIR'	,	#Kirguizistán
'LA': 'LAO'	,	#Laos
'LE': 'RL'    ,	#Líbano
'MY': 'MAL'	,	#Malasia
'MV': 'MDV'	,	#Maldivas
'MG': 'MOG'	,	#Mongolia
'BM': 'MYA'	,	#Myanmar (Birmania)
'NP': 'NEP'	,	#Nepal
'MU': 'OMN'	,	#Omán
'PK': 'PAK'	,	#Pakistán
'RP': 'RP'    ,	#Filipinas
'QA': 'Q'     ,	#Qatar
'SA': 'SA'    ,	#Arabia Saudita
'SN': 'SGP'	,	#Singapur
'CE': 'CL'    ,	#Sri Lanka
'SY': 'SYR'	,	#Siria
'TW': 'RC'    ,	#Taiwán
'TI': 'TAJ'	,	#Tadschikistan
'TH': 'THA'	,	#Tailandia
'TU': 'TR'    ,	#Turquía
'TX': 'TUR'	,	#Turkmenistan
'AE': 'UAE'	,	#Emiratos Arabes
'UZ': 'UZB'	,	#Uzbekistan
'VM': 'VN'    ,	#Vietnam
'YM': 'YMD'	,	#Yemen
'AG': 'DZ'    ,	#Argelia
'AO': 'ANG'	,	#Angola
'BN': 'RPH'	,	#Benin
'BC': 'RB'    ,	#Botswana
'UV': 'BF'    ,	#Burkina Faso
'BY': 'BU'    ,	#Burundi
'CM': 'CAM'	,	#Camerun
'CV': 'KVR'	,	#Cabo Verde
'CT': 'RCA'	,	#Central-Africa
'CD': 'CHA'	,	#Chad
'CN': 'KOM'	,	#Comoros
'CF': 'RCB'	,	#Congo (Brazzaville)
'CG': 'ZR'    ,	#Congo (Kinshasa)
'DJ': 'DH'    ,	#Djibouti
'EG': 'ET'    ,	#Egipto
'EK': 'AQG'	,	#Guinea ecuatorial
'ET': 'ETH'	,	#Etiopía
'GB': 'GAB'	,	#Gabón
'GA': 'GAM'	,	#Gambia
'GH': 'GH'    ,	#Ghana
'GV': 'GUI'	,	#Guinea
'PU': 'GBA'	,	#Guinea-Bissau
'IV': 'CI'    ,	#Costa de Marfil
'KE': 'EAK'	,	#Kenya
'LT': 'LS'    ,	#Lesotho
'LI': 'LB'    ,	#Liberia
'LY': 'LAR'	,	#Libia
'MA': 'RM'    ,	#Madagascar
'MI': 'MW'    ,	#Malawi
'ML': 'RMM'	,	#Mali
'MR': 'RIM'	,	#Mauritania
'MP': 'MS'    ,	#Mauricio
'MF': 'MY'    ,	#Mayotte
'MO': 'MA'    ,	#Marruecos
'MZ': 'MOZ'	,	#Mozambique
'WA': 'NAB'	,	#Namibia
'NG': 'RN'    ,	#Níger
'NI': 'WAN'	,	#Nigeria
'RE': 'REU'	,	#Reunión
'RW': 'RWA'	,	#Ruanda
'SH': 'SHA'	,	#Santa Helena
'TP': 'STP'	,	#Santo Tomé & Príncipe
'SG': 'SN'    ,	#Senegal
'SE': 'SY'    ,	#Seychelles
'SL': 'WAL'	,	#Sierra Leona
'SO': 'SP'    ,	#Somalia
'SF': 'ZA'    ,	#Sudáfrica
'SU': 'FS'    ,	#Sudán
'WZ': 'SD'    ,	#Swazilandia
'TZ': 'EAT'	,	#Tanzania
'TO': 'TG'    ,	#Togo
'TS': 'TN'    ,	#Túnez
'UG': 'EAV'	,	#Uganda
'ZA': 'Z'     ,	#Zambia
'ZI': 'ZW'    ,	#Zimbabwe
'AC': 'ANT'	,	#Antigua & Barbuda
'AR': 'RA'    ,	#Argentina
'AV': 'AGU'	,	#Anguilla
'BB': 'BDS'	,	#Barbados
'BD': 'BPA'	,	#Bermudas
'BF': 'BS'    ,	#Bahamas
'BH': 'BH'    ,	#Belice
'BL': 'BOL'	,	#Bolivia
'BR': 'BR'    ,	#Brasil
'CA': 'CDN'	,	#Canadá
'CI': 'RCH'	,	#Chile
'CJ': 'CAY'	,	#Islas Caimán
'CO': 'CO'    ,	#Colombia
'CS': 'CR'    ,	#Costa Rica
'CU': 'C'     ,	#Cuba
'DO': 'WD'    ,	#Dominica
'DR': 'DOM'	,	#República Dominicana
'EC': 'EC'    ,	#Ecuador
'ES': 'ES'    ,	#El Salvador
'FG': 'FGU'	,	#Guayana Fr.
'FK': 'FGB'	,	#Islas Malvinas
'GJ': 'WG'    ,	#Granada
'GL': 'GRO'	,	#Groenlandia
'GP': 'GKA'	,	#Guadalupe
'GT': 'GCA'	,	#Guatemala
'GY': 'GUY'	,	#Guyana
'HA': 'RH'    ,	#Haití
'HO': 'HON'	,	#Honduras
'JM': 'JA'    ,	#Jamaica
'MB': 'MQU'	,	#Martinique
'MH': 'MTT'	,	#Montserrat
'MX': 'MEX'	,	#México
'NS': 'SME'	,	#Suriname
'NU': 'NIC'	,	#Nicaragua
'PA': 'FPY'	,	#Paraguay
'PE': 'PE'    ,	#Perú
'PM': 'PA'    ,	#Panamá
'SB': 'SPM'	,	#San Pierre & Miquelon
'ST': 'STL'	,	#Santa Lucia
'TD': 'TT'    ,	#Trinidad & Tabago
'TK': 'TCO'	,	#Turcos & Caicos
'UY': 'U'     ,	#Uruguay
'VC': 'WV'    ,	#San Vincente & Granadinas
'VE': 'YV'    ,	#Venezuela
'VI': 'VRG'	,	#Is. Vírgenes
'AS': 'AUS'	,	#Australia
'BP': 'SOL'	,	#Islas Salomón
'CW': 'CSP'	,	#Islas Cook
'FJ': 'FJI'	,	#Fiji
'FP': 'FSP'	,	#Polinesia
'KR': 'KSP'	,	#Kiribati
'NC': 'NKP'	,	#Nueva Caledonia
'NE': 'NIU'	,	#Niue
'NF': 'NFI'	,	#Islas Norfolk
'NH': 'VAN'	,	#Vanuatu
'NR': 'NSP'	,	#Nauru
'NZ': 'NZ'    ,	#Nueva Zelanda
'PP': 'PNG'	,	#Papua Nueva Guinea
'PC': 'PSP'	,	#Pitcairn
'RM': 'MSH'	,	#Islas Marshall 
'TL': 'TSP'	,	#Tokelau
'TN': 'TGA'	,	#Tonga
'TV': 'TVL'	,	#Tuvalu
'WF': 'WFP'	,	#Wallis & Futuna
'WS': 'WS'    ,	#Samoa-oeste
'AL': 'AL'    ,	#Albania
'AN': 'AND'	,	#Andorra
'AU': 'A'     ,	#Austria
'BO': 'WRS'	,	#Bielorrusia
'BE': 'B'     ,	#Bélgica
'BK': 'BHG'	,	#Bosnia Herzegovina
'BU': 'BG'    ,	#Bulgaria
'HR': 'KRO'	,	#Croacia
'EZ': 'CS'    ,	#Checoslovaquia
'DA': 'DK'    ,	#Dinamarca
'EN': 'EST'	,	#Estonia
'FO': 'FOI'	,	#Islas Faroe
'FI': 'SF'    ,	#Finlandia
'FR': 'F'     ,	#Francia
'GM': 'D'     ,	#Alemania
'GR': 'GR'    ,	#Grecia
'HU': 'H'     ,	#Hungría
'IC': 'IS'    ,	#Islandia
'EI': 'IRL'	,	#Irlanda
'IT': 'I'     ,	#Italia
'LG': 'LET'	,	#Letonia
'LS': 'FL'    ,	#Liechtenstein
'LH': 'LIT'	,	#Lituania
'LU': 'L'     ,	#Luxemburgo
'MK': 'MAK'	,	#Macedonia
'MT': 'M'     ,	#Malta
'MD': 'MOL'	,	#Moldavia
'MN': 'MC'    ,	#Monaco
'NL': 'NL'    ,	#Países Bajos
'NO': 'N'     ,	#Noruega
'PL': 'PL'    ,	#Polonia
'PO': 'P'     ,	#Portugal
'RO': 'R'     ,	#Rumanía
'SM': 'RSM'	,	#San Marino
'YI': 'YU'    ,	#Serbia & Montenegro
'SI': 'SLO'	,	#Eslovenia
'SP': 'E'     ,	#España
'SW': 'S'     ,	#Suecia
'SZ': 'CH'    ,	#Suiza
'UP': 'UKR'	,	#Ucrania
'UK': 'GBE'	,	#Inglaterra
'UK': 'SCO'	,	#Inglaterra
'UK': 'NIR'	,	#Inglaterra
'RS': 'SSR'		#Rusia 
}

aaf_record = dict(name='',fname='',sex='*',date='',time='',place='',country='')
headA = "#A93"
sex = '*'

def export_chart(chart):
    name = chart.last if chart.last else '*'
    a93 = ":".join([headA,name])
    fname = chart.first if chart.first else '*'
    place = chart.city
    date,_,time = chart.date.partition('T')
    date = ".".join(reversed([d.lstrip('0') for d in date.split('-')])) 
    time = time[:5]
    country = ccodes[datab.get_code_from_name(chart.country)]
    achunk = ",".join([a93,fname,sex,date,time,place,country])
    return achunk

def export_table(table):
    chlist = datab.get_chartlist(table)
    chart = Chart()
    chunks = []
    for id,_,_ in chlist:
        datab.load_chart(tname, id, chart) 
        chunks.append(export_chart(chart))
    return chunks

if __name__ == '__main__':
    datab.easy_connect()
    tname = 'personal'
    chunks = export_table(tname)
    aafile = path.joinpath(path.expanduser(path('~')),"%s.aaf" % tname)
    f = open(aafile, 'w', encoding='utf-8')
    for ch in chunks:
        f.write(ch)
        f.write('\n')
    f.close()
    #print chunks


