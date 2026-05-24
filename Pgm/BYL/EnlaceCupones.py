import flet as ft
import hashlib
import hmac as _hmac_mod
import sqlite3
import webbrowser
from urllib.parse import quote
import os

DB = r"D:\Python\Data\BYL\GES_BYL.DB"
URL_VISOR = "http://127.0.0.1:8550/?id="               # Cambiar IP 192.168.0.25
WHATSAPP_NUM = "5493813561580"                         # <--CambiarNumeroCelular
wCntLleno = 10

try:
    wKeyCvt1 = os.environ['GBYL_KEY1']
except:
    wKeyCvt1 = "dvtcksqonz"
try:
    wKeyCvt2 = os.environ['GBYL_KEY2']
except:
    wKeyCvt2 = "ABCDEFGHIJ"

_CUPON_HMAC_KEY = os.environ.get("CUPON_HMAC_KEY", "")


def calcular_hmac_cupon(ev, sec) -> str:
    if not _CUPON_HMAC_KEY:
        return ""
    msg = f"{int(ev):05d}{int(sec):06d}".encode()
    return _hmac_mod.new(_CUPON_HMAC_KEY.encode(), msg, hashlib.sha256).hexdigest()[:8]


def asegurar_columna_adic():
    cnx = sqlite3.connect(DB)
    try:
        cnx.execute("ALTER TABLE INF_URL ADD COLUMN INF_ADIC TEXT")
        cnx.commit()
    except Exception:
        pass
    cnx.close()

                                                                    # UTILIDADES
def solo_numeros(txt):
    txt = str(txt or "").strip()
    return txt.isdigit()

def complemento_digito(c):
    if str(c).isdigit():
        return str(9 - int(c))
    return c

def complemento_char(c):
    mapa = { **{chr(i): chr(ord("Z") - (i - ord("A")))
             for i in range(ord("A"), ord("Z") + 1)},
             **{chr(i): chr(ord("z") - (i - ord("a")))
             for i in range(ord("a"), ord("z") + 1)},  }
    return mapa.get(c, c)

def transformar_texto(txt):
    resultado = ""

    for c in str(txt):
        if c.isdigit():
            resultado += complemento_digito(c)
        else:
            resultado += complemento_char(c)

    return resultado

def transformar_numero(num_str):
    num_str = str(num_str or "").strip()

    if not num_str:
        return ""

    resultado = complemento_digito(num_str[0])

    for i in range(1, len(num_str)):
        ant = int(num_str[i - 1])
        act = int(num_str[i])
        diff = act - ant

        if diff > 0:
            letra = chr(ord("A") + diff - 1)
        elif diff < 0:
            letra = chr(ord("a") + abs(diff) - 1)
        else:
            letra = "J"

        resultado += letra

    return resultado

def recuperar_numero(txt):
    txt = str(txt or "").strip()

    if txt == "":
        return ""

    if not txt[0].isdigit():
        return txt

    primer = str(9 - int(txt[0]))
    resultado = primer
    actual = int(primer)

    for ch in txt[1:]:
        if "A" <= ch <= "I":
            delta = ord(ch) - ord("A") + 1
        elif ch == "J":
            delta = 0
        elif "a" <= ch <= "i":
            delta = -(ord(ch) - ord("a") + 1)
        elif ch == "j":
            delta = 0
        else:
            return txt

        actual = actual + delta

        if actual < 0 or actual > 9:
            return txt

        resultado += str(actual)

    return resultado

def transformar(valor):
    if valor is None:
        return ""

    v = str(valor).strip()

    if v.isdigit():
        return transformar_numero(v)

    return transformar_texto(v)

def recuperar(valor_convertido, valor_original):
    v_conv = str(valor_convertido or "").strip()
    v_orig = str(valor_original or "").strip()

    if v_orig.isdigit():
        return recuperar_numero(v_conv)

    return transformar_texto(v_conv)

def convertirLista(wLista, wCar):
    global wLisNum, qchr, wPos, qVal
    if wLista[0] >= "0" and wLista[0] <= "9":
        return(wLista)
    else:
        if wCar == 2 or wCar == 4 or wCar == 6 or wCar == 8:
            wKeyCvt3 = wKeyCvt2
            wKeyCvt4 = wKeyCvt1
        else:
            wKeyCvt3 = wKeyCvt1
            wKeyCvt4 = wKeyCvt2
        wListCvt = ""
        for wIx1 in range(0, ((wCntLleno * 3) + 0), 3):
             qChr = wLista[wIx1:(wIx1 + 1)]
             wPos = wKeyCvt3.find(qChr)
             if wPos == 9:
                qVal = "0"
             else:
                qVal = str((wPos + 1))
             wListCvt = wListCvt + qVal
             qChr = wLista[(wIx1 + 1):(wIx1 + 2)]
             wPos = wKeyCvt4.find(qChr)
             if wPos == 9:
                qVal = "0_"
             else:
                qVal = str((wPos + 1)) + "_"
             wListCvt = wListCvt + qVal
        return(wListCvt)

def calc_mod10(txt):
    s_txt = "".join(ch for ch in str(txt or "") if ch.isdigit())

    if s_txt == "":
        return 0

    wSuma = 0
    wFact = 2

    for ch in reversed(s_txt):
        wVal = int(ch) * wFact

        if wVal > 9:
            wVal = (wVal // 10) + (wVal % 10)

        wSuma = wSuma + wVal

        if wFact == 2:
            wFact = 1
        else:
            wFact = 2

    return (10 - (wSuma % 10)) % 10

def generar_id_cupon(ev, sec):
    s_evn = str(ev or "").zfill(5)
    s_sec = str(sec or "").zfill(6)
    dv1 = calc_mod10(s_evn + s_sec)
    dv2 = calc_mod10(str(dv1) + s_sec + s_evn)
    return f"{s_evn}{s_sec}{dv1}{dv2}", dv1, dv2

def guardar_inf_url(ev, sec, dv1, dv2, data_txt):
    hmac_code = calcular_hmac_cupon(ev, sec)
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()

    try:
        cur.execute(
            """
            INSERT INTO INF_URL
                (INF_EVN, INF_SEC, INF_DV1, INF_DV2, INF_DTA, INF_ADIC)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (int(ev), int(sec), int(dv1), int(dv2), str(data_txt or ""), hmac_code or None), )

    except sqlite3.IntegrityError:
        cur.execute(
            """
            UPDATE INF_URL
               SET INF_DV1 = ?, INF_DV2 = ?, INF_DTA = ?, INF_ADIC = ?
             WHERE INF_EVN = ? AND INF_SEC = ?
            """,
            (int(dv1), int(dv2), str(data_txt or ""), hmac_code or None, int(ev), int(sec)), )

    cnx.commit()
    cnx.close()

                                                                 # BASE DE DATOS
def get_eventos():
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute( "SELECT EVN_NUM, EVN_DSC FROM EVN_DEF ORDER BY EVN_NUM" )
    rows = cur.fetchall()
    cnx.close()
    return rows

def get_matrices():
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute( "SELECT MTZ_NUM, MTZ_DSC FROM MTZ_DEF ORDER BY MTZ_NUM" )
    rows = cur.fetchall()
    cnx.close()
    return rows

def get_evento_desc(ev):
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute( "SELECT EVN_DSC FROM EVN_DEF WHERE EVN_NUM = ?",
                 (ev,),                                          )
    row = cur.fetchone()
    cnx.close()

    if not row:
        return ""

    return str(row[0] or "")

def get_matriz_desc(mtz):
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute( "SELECT MTZ_DSC FROM MTZ_DEF WHERE MTZ_NUM = ?",
                 (mtz,),                                          )
    row = cur.fetchone()
    cnx.close()

    if not row:
        return ""

    return str(row[0] or "")

def existe_evento(ev):
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute( "SELECT 1 FROM EVN_DEF WHERE EVN_NUM = ?",
                 (ev,),                                     )
    row = cur.fetchone()
    cnx.close()
    return row is not None

def existe_matriz(mtz):
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute( "SELECT 1 FROM MTZ_DEF WHERE MTZ_NUM = ?",
                 (mtz,),                                    )
    row = cur.fetchone()
    cnx.close()
    return row is not None

def get_cupon(ev, sec):
    cnx = sqlite3.connect(DB)
    cur = cnx.cursor()
    cur.execute(
        """
        Select EVNC_NUM, EVNC_SEC, EVNC_DES, EVNC_HAS, EVNC_GRP,
               EVNC_TPO, EVNC_EST, EVNC_TID, EVNC_NID, EVNC_NOM,
               EVNC_UBI, EVNC_DOM, EVNC_REF, EVNC_SOC, EVNC_TRN,
               EVNC_VEN, EVNC_SUB, A.MTZ_NUM, A.CAR_SER, A.CAR_NUM, B.CAR_LIS
          FROM EVNC_CAR A
          LEFT JOIN MTZ_CAR B
            ON B.MTZ_NUM = A.MTZ_NUM AND B.CAR_SER = A.CAR_SER
                                     AND B.CAR_NUM = A.CAR_NUM
         WHERE EVNC_NUM = ? AND EVNC_SEC = ?
         ORDER BY EVNC_SUB
        """,
        (ev, sec),                          )

    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    cnx.close()

    if not rows:
        return None

    data = dict(zip(cols, rows[0]))

    data["EVNC_TID"] = ( "TID" + str(sec)
                         if str(data.get("EVNC_TID") or "").strip() == ""
                         else data.get("EVNC_TID")                        )
    data["EVNC_NID"] = ( "NID" + str(sec)
                         if str(data.get("EVNC_NID") or "").strip() == ""
                         else data.get("EVNC_NID")                        )
    data["EVNC_NOM"] = ( "NOM" + str(sec)
                         if str(data.get("EVNC_NOM") or "").strip() == ""
                         else data.get("EVNC_NOM")                        )
    data["EVNC_UBI"] = ( "UBI" + str(sec)
                         if str(data.get("EVNC_UBI") or "").strip() == ""
                         else data.get("EVNC_UBI")                        )
    data["EVNC_DOM"] = ( "DOM" + str(sec)
                         if str(data.get("EVNC_DOM") or "").strip() == ""
                         else data.get("EVNC_DOM")                        )
    data["EVNC_REF"] = ( "REF" + str(sec)
                         if str(data.get("EVNC_REF") or "").strip() == ""
                         else data.get("EVNC_REF")                        )

    for i in range(1, 4):
        data[f"EVNC_SUB{i}"] = ""
        data[f"MTZ_NUM{i}"]  = ""
        data[f"CAR_SER{i}"]  = ""
        data[f"CAR_NUM{i}"]  = ""
        data[f"CAR_LIS{i}"]  = ""                                      #agregado

    for i, row in enumerate(rows[:3], start=1):
        reg = dict(zip(cols, row))
        wCarton = row[19]
        wLisNum = row[20]
        if wLisNum != "":
            wLisNum = convertirLista(wLisNum, wCarton)
      # wLisNum = wLisNum.replace(":", ".")
        data[f"EVNC_SUB{i}"] = reg.get("EVNC_SUB", "")
        data[f"MTZ_NUM{i}"]  = reg.get("MTZ_NUM",  "")
        data[f"CAR_SER{i}"]  = reg.get("CAR_SER",  "")
        data[f"CAR_NUM{i}"]  = reg.get("CAR_NUM",  "")
        data[f"CAR_LIS{i}"]  = wLisNum                                 #agregado

    return data

                                                                    # UI HELPERS
def fila_etiqueta_valor(etiqueta, control, ancho_etq=170):
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    etiqueta, weight=ft.FontWeight.BOLD, size=14, ),
                width=ancho_etq,                                   ),
            control,                                                ],
        spacing=8,                                                   )

def fila_ficha(etiqueta, control_valor, control_boton=None,
               control_desc=None):
    ctrls = [
        ft.Container(
            content=ft.Text(
                etiqueta, weight=ft.FontWeight.BOLD, size=14, ),
            width=170,                                          ),
        ft.Container(
            content=control_valor, width=110, ),
        ft.Container(
            content=control_boton if control_boton is not None else ft.Text(""),
            width=42,                                                           ),
        ft.Container(
            content=control_desc if control_desc is not None else ft.Text(""),
            expand=True,                                                      ), ]

    return ft.Row( controls=ctrls, spacing=8,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER, )


def main(page: ft.Page):
    page.title = "Enlace de Cupones"
    page.window_width = 760
    page.window_height = 780
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    asegurar_columna_adic()
    eventos = get_eventos()
    matrices = get_matrices()

    body = ft.Container(expand=True)
    page.add(body)

    txt_evento = ft.TextField(
        width=90, height=34, text_size=14, content_padding=8, )

    txt_desc_evento = ft.TextField(
        width=360, height=34, text_size=13, read_only=True, content_padding=8, )

    txt_matriz = ft.TextField(
        width=90, height=34, text_size=14, content_padding=8, )

    txt_desc_matriz = ft.TextField(
        width=360, height=34, text_size=13, read_only=True, content_padding=8, )

    txt_sec = ft.TextField(
        width=120, height=34, text_size=14, content_padding=8, )

    salida = ft.Text("", color=ft.Colors.RED_700)

    txt_original = ft.TextField(
        value="", multiline=True, min_lines=5, max_lines=8,
        read_only=True, width=680, text_size=14,            )

    txt_convertido = ft.TextField(
        value="", multiline=True, min_lines=5, max_lines=8,
        read_only=True, width=680, text_size=14,            )

    txt_recuperado = ft.TextField(
        value="", multiline=True, min_lines=5, max_lines=8,
        read_only=True, width=680, text_size=14,            )

    txt_url = ft.TextField(
        value="", multiline=True, min_lines=5, max_lines=10,
        read_only=True, width=680, text_size=14,            )

    try:
        estilo = ft.TextStyle(font_family="Courier New", size=14)
        txt_original.text_style = estilo
        txt_convertido.text_style = estilo
        txt_recuperado.text_style = estilo
        txt_url.text_style = estilo
    except Exception:
        pass

    def mostrar(control):
        body.content = control
        page.update()

    def copiar_texto(valor):
        try:
            page.set_clipboard(str(valor or ""))
            salida.value = "Copiado al portapapeles"
        except Exception:
            salida.value = "No se pudo copiar"
        page.update()

    def cargar_desc_evento():
        ev = str(txt_evento.value or "").strip()

        if ev.isdigit():
            txt_desc_evento.value = get_evento_desc(int(ev))
        else:
            txt_desc_evento.value = ""

        page.update()

    def cargar_desc_matriz():
        mtz = str(txt_matriz.value or "").strip()

        if mtz.isdigit():
            txt_desc_matriz.value = get_matriz_desc(int(mtz))
        else:
            txt_desc_matriz.value = ""

        page.update()

    def abrir_lista_codigos(datos, txt_codigo, txt_desc, titulo):
        lista = ft.Column(
            spacing=4, scroll=ft.ScrollMode.AUTO, height=260, )

        filtro = ft.TextField(
            width=280, height=34, text_size=13, content_padding=8, )

        pagina = {"desde": 0}
        por_pagina = 12
        info_pag = ft.Text("", size=12)
        dlg = None

        def seleccionar(num, dsc):
            txt_codigo.value = num
            txt_desc.value = dsc
            dlg.open = False
            page.update()

        def refrescar():
            lista.controls.clear()

            txt_f = str(filtro.value or "").strip().lower()

            filtrados = []
            for cod_num, cod_dsc in datos:
                s_num = str(cod_num).zfill(5)
                s_dsc = str(cod_dsc or "")
                if txt_f == "":
                    filtrados.append((s_num, s_dsc))
                else:
                    if txt_f in s_num.lower() or txt_f in s_dsc.lower():
                        filtrados.append((s_num, s_dsc))

            total = len(filtrados)
            desde = pagina["desde"]

            if desde >= total and total > 0:
                pagina["desde"] = max(total - por_pagina, 0)
                desde = pagina["desde"]

            hasta = desde + por_pagina
            tramo = filtrados[desde:hasta]

            for s_num, s_dsc in tramo:
                lista.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(s_num, width=70, size=13),
                            ft.Text(s_dsc, width=300, size=13),
                            ft.ElevatedButton( "Sel", height=30,
                                on_click=lambda e, n=s_num, d=s_dsc:
                                    seleccionar(n, d),              ), ],
                        spacing=6,                                       ) )

            if total == 0:
                info_pag.value = "Sin coincidencias"
            else:
                info_pag.value = (
                    f"{desde + 1} a {min(hasta, total)} de {total}" )

            page.update()

        def anterior(e):
            if pagina["desde"] >= por_pagina:
                pagina["desde"] -= por_pagina
                refrescar()

        def siguiente(e):
            txt_f = str(filtro.value or "").strip().lower()

            filtrados = []
            for cod_num, cod_dsc in datos:
                s_num = str(cod_num).zfill(5)
                s_dsc = str(cod_dsc or "")
                if txt_f == "":
                    filtrados.append((s_num, s_dsc))
                else:
                    if txt_f in s_num.lower() or txt_f in s_dsc.lower():
                        filtrados.append((s_num, s_dsc))

            if pagina["desde"] + por_pagina < len(filtrados):
                pagina["desde"] += por_pagina
                refrescar()

        def cerrar_dlg(e=None):
            dlg.open = False
            page.update()

        filtro.on_change = lambda e: ( pagina.__setitem__("desde", 0),
                                       refrescar()                    )

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Column(
                controls=[
                    fila_etiqueta_valor("Filtro:", filtro, ancho_etq=70),
                    lista,
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Anterior", on_click=anterior),
                            ft.ElevatedButton("Siguiente", on_click=siguiente),
                            info_pag,
                            ft.ElevatedButton("Cancelar", on_click=cerrar_dlg), ],
                        spacing=8,                                               ), ],
                spacing=8, tight=True,                                                ), )

        if dlg not in page.overlay:
            page.overlay.append(dlg)

        dlg.open = True
        refrescar()
        page.update()

    btn_evento = ft.ElevatedButton(
        "...", width=36, height=34,
        on_click=lambda e: abrir_lista_codigos(
            eventos, txt_evento, txt_desc_evento, "Lista de Eventos" ), )

    btn_matriz = ft.ElevatedButton(
        "...", width=36, height=34,
        on_click=lambda e: abrir_lista_codigos(
            matrices, txt_matriz, txt_desc_matriz, "Lista de Matrices" ), )

    def volver_inicio(e=None):
        mostrar(vista_principal())

    def abrir_visor(e=None):
        url = str(txt_url.value or "").strip()

        if not url:
            salida.value = "Primero confirmar datos"
            page.update()
            return

        webbrowser.open(url)

    def compartir_whatsapp(e=None):
        url = str(txt_url.value or "").strip()

        if not url:
            salida.value = "Primero confirmar datos"
            page.update()
            return

        url = url.replace("\n", "").replace("\r", "").strip()
        wMsg = quote(url, safe="")
        wUrl = f"https://wa.me/{WHATSAPP_NUM}?text={wMsg}"
        webbrowser.open(wUrl)

    def procesar(e):
        ev = str(txt_evento.value or "").strip()
        mtz = str(txt_matriz.value or "").strip()
        sec = str(txt_sec.value or "").strip()

        if not solo_numeros(ev):
            salida.value = "Evento inválido"
            page.update()
            return

        if not solo_numeros(mtz):
            salida.value = "Matriz inválida"
            page.update()
            return

        if not solo_numeros(sec):
            salida.value = "Secuencia inválida"
            page.update()
            return

        ev_num = int(ev)
        mtz_num = int(mtz)
        sec_num = int(sec)

        if ev_num < 1 or ev_num > 99999:
            salida.value = "Evento fuera de rango"
            page.update()
            return

        if mtz_num < 1 or mtz_num > 99999:
            salida.value = "Matriz fuera de rango"
            page.update()
            return

        if sec_num < 1 or sec_num > 999999:
            salida.value = "Secuencia fuera de rango"
            page.update()
            return

        if not existe_evento(ev_num):
            salida.value = "Evento no existe"
            page.update()
            return

        if not existe_matriz(mtz_num):
            salida.value = "Matriz no existe"
            page.update()
            return

        txt_desc_evento.value = get_evento_desc(ev_num)
        txt_desc_matriz.value = get_matriz_desc(mtz_num)

        data = get_cupon(ev_num, sec_num)

        if not data:
            salida.value = "No existe cupón"
            page.update()
            return

        salida.value = ""
        mostrar_detalle(data)

    def mostrar_detalle(data):
        campos = list(data.items())

        lista = ft.Column(
            controls=[
                fila_etiqueta_valor(
                    f"{k}:",
                    ft.Text(str(v) if v is not None else ""), )
                for k, v in campos                             ],
            spacing=6,                                           )

        def copiar(texto):
            try:
                page.set_clipboard(texto)
                salida.value = "Copiado ✔"
            except Exception:
                salida.value = "Error al copiar"
            page.update()

        def confirmar(e):
            valores_originales = [ str(v).strip() if v is not None else ""
                                   for _, v in campos                     ]

            cadena_original = "datos=" + "~".join(valores_originales)

            valores_convertidos = [ transformar(v) for _, v in campos ]

            cadena_convertida = "datos=" + "~".join(valores_convertidos)

            valores_recuperados = [ recuperar(v_conv, v_orig)
                                    for (_, v_orig), v_conv
                                    in zip(campos, valores_convertidos) ]

            cadena_recuperada = "datos=" + "~".join(valores_recuperados)

            txt_original.value = cadena_original
            txt_convertido.value = cadena_convertida
            txt_recuperado.value = cadena_recuperada

            data_guardar = "~".join(valores_convertidos)
            url_id, dv1, dv2 = generar_id_cupon( data.get("EVNC_NUM", ""),
                                                 data.get("EVNC_SEC", ""), )
            guardar_inf_url( data.get("EVNC_NUM", "0"),
                             data.get("EVNC_SEC", "0"),
                             dv1, dv2, data_guardar,   )
            txt_url.value = URL_VISOR + url_id

            page.update()

        vista = ft.Column(
            controls=[
                ft.Text("Datos del Cupón", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10), lista, ft.Container(height=14),
               ft.Row(
                    controls=[
                        ft.ElevatedButton("Confirmar", on_click=confirmar),
                        ft.ElevatedButton("Ver Visor", on_click=abrir_visor),
                        ft.ElevatedButton("WhatsApp", on_click=compartir_whatsapp),
                        ft.ElevatedButton("Cancelar", on_click=volver_inicio), ],
                    spacing=12,                                                  ),
                ft.Container(height=16),
                                                                      # ORIGINAL
                ft.Row(
                    controls=[
                        ft.Text("Cadena original:", weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton( "Copiar",
                            on_click=lambda e: copiar(txt_original.value), ), ] ),
                txt_original,
                ft.Container(height=10),
                                                                    # CONVERTIDA
                ft.Row(
                    controls=[
                        ft.Text("Cadena convertida:", weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton( "Copiar",
                            on_click=lambda e: copiar(txt_convertido.value), ), ] ),
                txt_convertido,
                ft.Container(height=10),
                                                                           # URL
                ft.Row(
                    controls=[
                        ft.Text("URL visor:", weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton( "Copiar",
                            on_click=lambda e: copiar(txt_url.value), ), ] ),
                txt_url,
                ft.Container(height=10),
                                                                    # RECUPERADA
                ft.Row(
                    controls=[
                        ft.Text("Cadena recuperada:", weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton( "Copiar",
                            on_click=lambda e: copiar(txt_recuperado.value), ), ] ),
                txt_recuperado,                                                    ],
            spacing=8, scroll=ft.ScrollMode.AUTO,                                    )

        mostrar(vista)

    async def cerrar(e):
        await page.window.close()

    def vista_principal():
        return ft.Column(
            controls=[
                ft.Text( "Enlaces de Cupones", size=20,
                         weight=ft.FontWeight.BOLD, ),
                ft.Container(height=12),

                fila_ficha( "Número de Evento:",
                            txt_evento, btn_evento, txt_desc_evento, ),

                fila_ficha( "Número de Matriz:",
                            txt_matriz, btn_matriz, txt_desc_matriz, ),

                fila_ficha( "Número de Secuencia:",
                            txt_sec, None, None,   ),

                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.ElevatedButton( "Procesar", on_click=procesar, ),
                        ft.ElevatedButton( "Finalizar", on_click=cerrar,  ), ],
                    spacing=12,                                                 ),
                ft.Container(height=12),
                salida,                                                          ],
            spacing=8,                                                             )

    txt_evento.on_blur = lambda e: cargar_desc_evento()
    txt_matriz.on_blur = lambda e: cargar_desc_matriz()
    mostrar(vista_principal())


ft.app(target=main)