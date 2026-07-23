# -*- coding: utf-8 -*-
import sys,os
import gtk
import datetime
import re
import astronex.state as state
from .. utils import degtodec
curr = None

mstar_bugloc = { 'Jaen': 'Jaén', 
        'Almeria': 'Almería', 
        'Avila': 'Ávila',
        'Cadiz': 'Cádiz',
        'Caceres': 'Cáceres',
        'Cordoba': 'Córdoba',
        'Leon': 'León',
        'Malaga': 'Málaga',
        'L Palmas de Gran Canaria': 'Las Palmas de Gran Canaria' }

ccodes = {
'AFG':'AF'	,	#Afganistán
'ARM':'AM'	,	#Armenia
'ASB':'AJ'	,	#Azerbaiján
'BRN':'BA'	,	#Bahrain
'BD' :'BG'  ,	#Bangla Desh
'BHU':'BT'	,	#Bhután
'BRU':'BX'	,	#Brunei
'K'  :'CB'  ,	#Camboya
'TJ' :'CH'  ,	#China
'CY' :'CY'  ,	#Chipre
'GRG':'GG'	,	#Georgia
'HKG':'HK'	,	#Hong Kong
'IND':'IN'	,	#India
'RI' :'ID'  ,	#Indonesia
'IR' :'IR'  ,	#Irán
'IRQ':'IZ'	,	#Irak
'IL' :'IS'  ,	#Israel
'J'  :'JA'  ,	#Japón
'JOR':'JO'	,	#Jordania
'KAZ':'KZ'	,	#Kazajstán
'KOR':'KN'	,	#Corea del Norte
'ROK':'KS'	,	#Corea del Sur
'KWT':'KU'	,	#Kuwait
'KIR':'KG'	,	#Kirguizistán
'LAO':'LA'	,	#Laos
'RL' :'LE'  ,	#Líbano
'MAL':'MY'	,	#Malasia
'MDV':'MV'	,	#Maldivas
'MOG':'MG'	,	#Mongolia
'MYA':'BM'	,	#Myanmar (Birmania)
'NEP':'NP'	,	#Nepal
'OMN':'MU'	,	#Omán
'PAK':'PK'	,	#Pakistán
'RP' :'RP'  ,	#Filipinas
'Q'  :'QA'  ,	#Qatar
'SA' :'SA'  ,	#Arabia Saudita
'SGP':'SN'	,	#Singapur
'CL' :'CE'  ,	#Sri Lanka
'SYR':'SY'	,	#Siria
'RC' :'TW'  ,	#Taiwán
'TAJ':'TI'	,	#Tadschikistan
'THA':'TH'	,	#Tailandia
'TR' :'TU'  ,	#Turquía
'TUR':'TX'	,	#Turkmenistan
'UAE':'AE'	,	#Emiratos Arabes
'UZB':'UZ'	,	#Uzbekistan
'VN' :'VM'  ,	#Vietnam
'YMD':'YM'	,	#Yemen
'DZ' :'AG'  ,	#Argelia
'ANG':'AO'	,	#Angola
'RPH':'BN'	,	#Benin
'RB' :'BC'  ,	#Botswana
'BF' :'UV'  ,	#Burkina Faso
'BU' :'BY'  ,	#Burundi
'CAM':'CM'	,	#Camerun
'KVR':'CV'	,	#Cabo Verde
'RCA':'CT'	,	#Central-Africa
'CHA':'CD'	,	#Chad
'KOM':'CN'	,	#Comoros
'RCB':'CF'	,	#Congo (Brazzaville)
'ZR' :'CG'  ,	#Congo (Kinshasa)
'DH' :'DJ'  ,	#Djibouti
'ET' :'EG'  ,	#Egipto
'AQG':'EK'	,	#Guinea ecuatorial
'ETH':'ET'	,	#Etiopía
'GAB':'GB'	,	#Gabón
'GAM':'GA'	,	#Gambia
'GH' :'GH'  ,	#Ghana
'GUI':'GV'	,	#Guinea
'GBA':'PU'	,	#Guinea-Bissau
'CI' :'IV'  ,	#Costa de Marfil
'EAK':'KE'	,	#Kenya
'LS' :'LT'  ,	#Lesotho
'LB' :'LI'  ,	#Liberia
'LAR':'LY'	,	#Libia
'RM' :'MA'  ,	#Madagascar
'MW' :'MI'  ,	#Malawi
'RMM':'ML'	,	#Mali
'RIM':'MR'	,	#Mauritania
'MS' :'MP'  ,	#Mauricio
'MY' :'MF'  ,	#Mayotte
'MA' :'MO'  ,	#Marruecos
'MOZ':'MZ'	,	#Mozambique
'NAB':'WA'	,	#Namibia
'RN' :'NG'  ,	#Níger
'WAN':'NI'	,	#Nigeria
'REU':'RE'	,	#Reunión
'RWA':'RW'	,	#Ruanda
'SHA':'SH'	,	#Santa Helena
'STP':'TP'	,	#Santo Tomé & Príncipe
'SN' :'SG'  ,	#Senegal
'SY' :'SE'  ,	#Seychelles
'WAL':'SL'	,	#Sierra Leona
'SP' :'SO'  ,	#Somalia
'ZA' :'SF'  ,	#Sudáfrica
'FS' :'SU'  ,	#Sudán
'SD' :'WZ'  ,	#Swazilandia
'EAT':'TZ'	,	#Tanzania
'TG' :'TO'  ,	#Togo
'TN' :'TS'  ,	#Túnez
'EAV':'UG'	,	#Uganda
'Z'  :'ZA'  ,	#Zambia
'ZW' :'ZI'  ,	#Zimbabwe
'ANT':'AC'	,	#Antigua & Barbuda
'RA' :'AR'  ,	#Argentina
'AGU':'AV'	,	#Anguilla
'BDS':'BB'	,	#Barbados
'BPA':'BD'	,	#Bermudas
'BS' :'BF'  ,	#Bahamas
'BH' :'BH'  ,	#Belice
'BOL':'BL'	,	#Bolivia
'BR' :'BR'  ,	#Brasil
'CDN':'CA'	,	#Canadá
'RCH':'CI'	,	#Chile
'CAY':'CJ'	,	#Islas Caimán
'CO' :'CO'  ,	#Colombia
'CR' :'CS'  ,	#Costa Rica
'C'  :'CU'  ,	#Cuba
'WD' :'DO'  ,	#Dominica
'DOM':'DR'	,	#República Dominicana
'EC' :'EC'  ,	#Ecuador
'ES' :'ES'  ,	#El Salvador
'FGU':'FG'	,	#Guayana Fr.
'FGB':'FK'	,	#Islas Malvinas
'WG' :'GJ'  ,	#Granada
'GRO':'GL'	,	#Groenlandia
'GKA':'GP'	,	#Guadalupe
'GCA':'GT'	,	#Guatemala
'GUY':'GY'	,	#Guyana
'RH' :'HA'  ,	#Haití
'HON':'HO'	,	#Honduras
'JA' :'JM'  ,	#Jamaica
'MQU':'MB'	,	#Martinique
'MTT':'MH'	,	#Montserrat
'MEX':'MX'	,	#México
'SME':'NS'	,	#Suriname
'NIC':'NU'	,	#Nicaragua
'FPY':'PA'	,	#Paraguay
'PE' :'PE'  ,	#Perú
'PA' :'PM'  ,	#Panamá
'SPM':'SB'	,	#San Pierre & Miquelon
'STL':'ST'	,	#Santa Lucia
'TT' :'TD'  ,	#Trinidad & Tabago
'TCO':'TK'	,	#Turcos & Caicos
'U'  :'UY'  ,	#Uruguay
'WV' :'VC'  ,	#San Vincente & Granadinas
'YV' :'VE'  ,	#Venezuela
'VRG':'VI'	,	#Is. Vírgenes
'AUS':'AS'	,	#Australia
'SOL':'BP'	,	#Islas Salomón
'CSP':'CW'	,	#Islas Cook
'FJI':'FJ'	,	#Fiji
'FSP':'FP'	,	#Polinesia
'KSP':'KR'	,	#Kiribati
'NKP':'NC'	,	#Nueva Caledonia
'NIU':'NE'	,	#Niue
'NFI':'NF'	,	#Islas Norfolk
'VAN':'NH'	,	#Vanuatu
'NSP':'NR'	,	#Nauru
'NZ' :'NZ'  ,	#Nueva Zelanda
'PNG':'PP'	,	#Papua Nueva Guinea
'PSP':'PC'	,	#Pitcairn
'MSH':'RM'	,	#Islas Marshall 
'TSP':'TL'	,	#Tokelau
'TGA':'TN'	,	#Tonga
'TVL':'TV'	,	#Tuvalu
'WFP':'WF'	,	#Wallis & Futuna
'WS' :'WS'  ,	#Samoa-oeste
'AL' :'AL'  ,	#Albania
'AND':'AN'	,	#Andorra
'A'  :'AU'  ,	#Austria
'WRS':'BO'	,	#Bielorrusia
'B'  :'BE'  ,	#Bélgica
'BHG':'BK'	,	#Bosnia Herzegovina
'BG' :'BU'  ,	#Bulgaria
'KRO':'HR'	,	#Croacia
'CS' :'EZ'  ,	#Checoslovaquia
'DK' :'DA'  ,	#Dinamarca
'EST':'EN'	,	#Estonia
'FOI':'FO'	,	#Islas Faroe
'SF' :'FI'  ,	#Finlandia
'F'  :'FR'  ,	#Francia
'D'  :'GM'  ,	#Alemania
'GR' :'GR'  ,	#Grecia
'H'  :'HU'  ,	#Hungría
'IS' :'IC'  ,	#Islandia
'IRL':'EI'	,	#Irlanda
'I'  :'IT'  ,	#Italia
'LET':'LG'	,	#Letonia
'FL' :'LS'  ,	#Liechtenstein
'LIT':'LH'	,	#Lituania
'L'  :'LU'  ,	#Luxemburgo
'MAK':'MK'	,	#Macedonia
'M'  :'MT'  ,	#Malta
'MOL':'MD'	,	#Moldavia
'MC' :'MN'  ,	#Monaco
'NL' :'NL'  ,	#Países Bajos
'N'  :'NO'  ,	#Noruega
'PL' :'PL'  ,	#Polonia
'P'  :'PO'  ,	#Portugal
'R'  :'RO'  ,	#Rumanía
'RSM':'SM'	,	#San Marino
'YU' :'YI'  ,	#Serbia & Montenegro
'SLO':'SI'	,	#Eslovenia
'E'  :'SP'  ,	#España
'S'  :'SW'  ,	#Suecia
'CH' :'SZ'  ,	#Suiza
'UKR':'UP'	,	#Ucrania
'GBE':'UK'	,	#Inglaterra
'SCO':'UK'	,	#Inglaterra
'NIR':'UK'	,	#Inglaterra
'SSR':'RS'	}	#Rusia 
#US	Estados Unidos
usa = {
'New York': 'Nueva York',
'South Carolina': 'Carolina del Sur',
'North Carolina': 'Carolina del Norte'}

brackets = re.compile(r' \[.*\]?')

class Console(gtk.VBox):
    def __init__(self,font):
        gtk.VBox.__init__(self, spacing=2)
        self.set_border_width(2)
        self.scrolledwin = gtk.ScrolledWindow()
        self.scrolledwin.show()
        self.pack_start(self.scrolledwin, padding=1)
        self.text = gtk.TextView()
        self.text.set_editable(True)
        self.text.set_wrap_mode(gtk.WRAP_WORD)
        self.scrolledwin.add(self.text)
        self.buffer = self.text.get_buffer() 
        self.end = self.buffer.create_mark('end',self.buffer.get_end_iter(),False)
        font = font.split(" ")[0].rstrip()+" 10"
        self.normal = self.buffer.create_tag('Normal', font=font, foreground='black')
        self.error = self.buffer.create_tag('Error', font=font, foreground='red') 
        self.warning = self.buffer.create_tag('Warning', font=font, foreground='blue') 
        self.buffer.insert_at_cursor(_("(La importacion puede tardar un poco...)\n")) 

def cust_cap(s):
    if s not in ['de','del','am','an','der','sous','im','bei','sur']:
        return s.capitalize()
    else:
        return s

def fix_tname(tn):
    tn = tn.replace(' ','_')
    if tn != '':
        while not tn[0].isalpha():
            tn = tn[1:]
        truetn = tn
        for let in tn:
            if not let.isalnum() and let != '_':
                truetn.replace(let,'')
        return truetn
    else:
        return tn


def parse_aaf(file,tname,con,sim,browser,encoding):
    from sqlite3 import DatabaseError
    doubt = []
    n = 0
    buf = con.buffer
    err = con.error; warn = con.warning
    try:
        with open(file, 'r', encoding=encoding) as source:
            lines = list(source)
    except IOError:
        buf.insert_with_tags(end,_("Error abriendo el archivo %s") % (file),err)
        return
    pending = False
    buf.set_text('')
    if not sim:
        curr.datab.create_table(tname)
        buf.insert_at_cursor(_("Creada tabla %s\n") % (tname))
    for line in lines:
        start,end = buf.get_bounds()
        if line.startswith('#A93'): 
            loc = state.Locality()
            a = line[5:].split(',')
            if a[2] not in ['M','F'] and a[3] in ['M','F']:
                line = line.replace(',','',1)
                a = line[5:].split(',')
            last = a[0].strip(); first=a[1].strip()
            date=a[3][:-1]; time=a[4]
            city=a[5].strip(); ccode=a[6].strip()
            last=last.replace('*','')
            first = first.replace('*','')
            city = brackets.sub('',city)
            city = city.split('/')[0]
            city = city.split('-')[0]
            city = city.lower()
            city = ' '.join([cust_cap(s) for s in city.split(' ')]) 
            try:
                # AAF country codes are text in Python 3.  The old
                # ``.decode('utf8')`` both crashes and obscures whether this
                # code has already been translated to Astro-Nex's database
                # code.
                ccode = ccodes[ccode]
            except KeyError:
                if ccode.find('-') == -1:
                    ccode = brackets.sub('',ccode)
                    ccode = ccode.strip()
                    if ccode != '':
                        city = ccode + ' ' + city
                    ccode,count = a[7].split('-') 
                else:
                    ccode,count = ccode.split('-')
            city = city.strip()
            if city in mstar_bugloc:
                city = mstar_bugloc[city]
            if ccode.startswith('US'):
                loc=curr.datab.fetch_blindly_usacity(ccode[-2:],city,loc)
            else: 
                loc = curr.datab.fetch_blindly(ccode,city,loc) 
            if not isinstance(loc,state.Locality):
                buf.insert_with_tags(end,"%s\n" % (loc),err)
                pending = True
                continue
            curr.date.settz(loc.zone) 
            d,m,y = date.split('.')
            h,mi,s = time.split(':')
            dt = datetime.datetime(int(y),int(m),int(d),int(h),int(mi),int(s))
            dt = datetime.datetime.combine(dt.date(),dt.time())
            curr.loc = loc
            curr.date.setdt(dt)
            curr.person.first = first; curr.person.last = last
            curr.setchart()
            if not sim:
                try:
                    curr.datab.store_chart(tname, curr.charts['calc'])
                except DatabaseError:
                    curr.charts['calc'].first += str(n+1).rjust(3,'0')
                    curr.datab.store_chart(tname, curr.charts['calc'])
            buf.insert_at_cursor(_("Importando %s %s\n") % (first,last))
            con.text.scroll_to_mark(buf.get_insert(),0.0,True,0.0,0.0)
            n += 1
            while (gtk.events_pending()):
                gtk.main_iteration()
        elif pending and line.startswith('#B93'): 
            loc = state.Locality()
            b = line[5:].split(',')
            lt1,lt2 = b[1].split(':');lg1, lg2= b[2].split(':') 
            lgs = lg1[-3]; lg = lg1[0:-3]+lg1[-2:]+lg2
            if lgs == 'E': lgs = '-'
            else: lgs = ''
            lts = lt1[-3]; lt = lt1[0:-3]+lt1[-2:]+lt2
            if lts == 'S': lts = '-'
            else: lts = ''
            lgs += lg; lts += lt
            loc.longitud = lgs; loc.latitud = lts
            loc.latdec = degtodec(loc.latitud)
            loc.longdec = degtodec(loc.longitud)
            loc.city = city
            loc.country_code = ccode
            count = count.strip()
            if ccode.startswith('US'):
                loc.country = 'USA'
            elif count in ['Escocia']:
                loc.country = 'Gran Bretaña'
            else:
                loc.country = count 
            if ccode.startswith('US'):
                if count in ['New York','South Carolina','Noth Carolina']:
                    count = usa[count]
                st,code = curr.datab.get_usa_state_code(count)
                curr.datab.fetch_blindly_zone_usa(st,code,loc)
            else:
                curr.datab.fetch_blindly_zone(loc)
            pending = False
            doubt.append("%s %s: %s" % (first,last,city))
            curr.date.settz(loc.zone) 
            d,m,y = date.split('.')
            h,mi,s = time.split(':')
            dt = datetime.datetime(int(y),int(m),int(d),int(h),int(mi),int(s))
            dt = datetime.datetime.combine(dt.date(),dt.time())
            curr.loc = loc
            curr.date.setdt(dt)
            curr.person.first = first; curr.person.last = last
            curr.setchart()
            if not sim:
                try:
                    curr.datab.store_chart(tname, curr.charts['calc'])
                except DatabaseError:
                    curr.charts['calc'].first += str(n+1).rjust(3,'0')
                    curr.datab.store_chart(tname, curr.charts['calc'])
            buf.insert_at_cursor(_("Importando %s %s\n") % (first,last))
            n += 1
            con.text.scroll_to_mark(buf.get_insert(),0.0,True,0.0,0.0)
            while (gtk.events_pending()):
                gtk.main_iteration()
    #end
    if not sim:
        browser.tables.emit('changed')
        browser.relist(tname)
    else:
        buf.insert_at_cursor('\nImportacion terminada en modo simulacion\n')
    start,end = buf.get_bounds()
    buf.create_mark('mess',end,True)
    buf.insert_with_tags(end,'\n*******\n',warn)
    buf.insert_at_cursor(_("Cartas importadas: %s; dudosas: %s") % (n,len(doubt)))
    buf.insert_at_cursor('(%.2f%%) \n' % (100*len(doubt)/float(n)))
    buf.insert_at_cursor(_("Las cartas siguientes fueron importadas sin encontrar\n"))
    buf.insert_at_cursor(_("la localidad correspondiente, y la zona horaria sera\n"))
    buf.insert_at_cursor(_("probablemente incorrrecta. Puede editar este panel,\n"))
    buf.insert_at_cursor(_("y copiar su contenido (menu clic derecho).")) 
    start,end = buf.get_bounds()
    buf.insert_with_tags(end,'\n*******\n',warn)
    for d in doubt:
        buf.insert_with_tags(end,'%s\n' % d,warn)
    con.text.scroll_to_mark(buf.get_mark('mess'),0.0,True,0.0,0.0)


def dlg_response(ibut,entry,tentry,con,but,enc,browser):
    file = ''; tn = ''
    codes = ['cp1252','utf-8']
    file = entry.get_text()
    tname = tentry.get_text()
    tn = fix_tname(tname)
    if entry.get_text() == '' or tn == '':
        return
    else: 
        tablelist = curr.datab.get_databases() 
        simul = but.get_active()
        if not simul:
            if tn in tablelist:
                result = replacedialog(tn)
                if result != gtk.RESPONSE_OK:
                    return 
        encoding = codes[enc.get_active()]
        #print encoding
        parse_aaf(file,tn,con,simul,browser,encoding)

def on_browse_but(but,entry):
    dialog = gtk.FileChooserDialog("Abrir archivo...",
                                None,
                                gtk.FILE_CHOOSER_ACTION_OPEN,
                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    dialog.set_default_response(gtk.RESPONSE_OK)

    filter = gtk.FileFilter()
    filter.set_name(_("Archivo AAF"))
    filter.add_mime_type("text/plain")
    filter.add_pattern("*.aaf")
    dialog.add_filter(filter)
    dialog.set_current_folder(os.path.expanduser("~"))

    filename = None
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
        filename = dialog.get_filename()
    elif response == gtk.RESPONSE_CANCEL:
        pass
    dialog.destroy()
    if filename is not None and filename != '':
        entry.set_text(filename) 
    return

def replacedialog(tbl):
    msg = _("La tabla %s existe. Reemplazarla, perdiendo los datos?") % tbl
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
            gtk.MESSAGE_WARNING,
            gtk.BUTTONS_OK_CANCEL, msg);
    result = dialog.run()
    dialog.destroy()
    return result


def export_chart(ch):
    aaf = "%s,%s,%s,%s,%s,%s,%s,%s,%s"
    aaf = aaf % (ch.last,ch.first,ch.date,ch.city,ch.region,ch.country,ch.zone,ch.latitud,ch.longitud)
    return aaf

#A93:Afa144,Edgar Allan,M,19.01.1809g,01:48:00,Boston,USMA-Massachusetts 
#B93:*,42N21:00,071W03:00,05hw00,0

class ImportPanel(gtk.HBox):
    def __init__(self,parent):
        global curr
        curr = parent.boss.get_state()
        browser = parent.mpanel.browser
        gtk.HBox.__init__(self)
        cons = Console(browser.font)
        
        frame = gtk.Frame()
        table = gtk.Table(2,4,True)
        label = gtk.Label(_('Importar archivo: '))
        entry = gtk.Entry()
        button = gtk.Button(_('Examinar'))
        button.connect('clicked',on_browse_but,entry)
        table.attach(label,0,1,0,1)
        table.attach(entry,1,2,0,1)
        table.attach(button,2,3,0,1)
        
        label = gtk.Label(_('Nombre tabla: '))
        tentry = gtk.Entry()
        tentry.set_text('importemp')
        button = gtk.CheckButton(_('Simular'))
        button.set_active(True)
        table.attach(label,0,1,1,2)
        table.attach(tentry,1,2,1,2)
        table.attach(button,2,3,1,2)
        
        encoding = gtk.RadioButton(None,'Win-1252')
        encoding.set_active(True)
        table.attach(encoding,3,4,0,1)
        encoding = gtk.RadioButton(encoding,'utf-8')
        table.attach(encoding,3,4,1,2)
    
        frame.add(table)
        vbox = gtk.VBox()
        vbox.pack_start(frame,False,False)
        vbox.pack_start(cons) 
        ibutton = gtk.Button(_('Importar'))
        ibutton.connect("clicked",dlg_response,entry,tentry,cons,button,encoding,browser)
        hbox = gtk.HBox()
        hbox.pack_end(ibutton,False,False)    
        vbox.pack_start(hbox,False,False)    
        frame = gtk.Frame()
        frame.set_border_width(6)
        frame.add(vbox)
        self.add(frame)
