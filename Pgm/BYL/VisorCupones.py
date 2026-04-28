# Name:        VisorCupones.py
# Purpose:     Visualiza la informacion de los Cupones y resultado de Sorteos
# Author:      Pedro / Adaptado
# Created:     09/04/2026
# Copyright:   (c) Pedro 2026
#
import flet as ft
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from urllib.parse import parse_qs, unquote, urlparse
import random
import os
import sqlite3
import base64
import mimetypes
import pygame
from datetime import datetime

DB = r"D:\Python\Data\BYL\GES_BYL.DB"
                                                                      # CONTEXTO
@dataclass
class CtxCupon:
    raw_url_data: str = ""
    url_id: str = ""
    msg_error: str = ""
    dbg_url: Dict[str, str] = field(default_factory=dict)

    cnx: object = None
    crs: object = None
    crs2: object = None
    evento: str = ""
    secuencia: str = ""
    vig_desde: str = ""
    vig_hasta: str = ""

    ctl_integ1: str = ""
    ctl_integ2: str = ""
    ctl_integ3: str = ""

    tpoIdentidad: str = ""
    nroIdentidad: str = ""
    nombre: str = ""
    localidad: str = ""
    domicilio: str = ""
    referencia: str = ""

    socioVinc: str = ""
    vendedor: str = ""

    subsec1: str = ""
    refcmb1: str = ""
    lisnum1: str = ""

    subsec2: str = ""
    refcmb2: str = ""
    lisnum2: str = ""

    subsec3: str = ""
    refcmb3: str = ""
    lisnum3: str = ""

    chn1_lin1: List[str] = field(default_factory=list)
    chn1_lin2: List[str] = field(default_factory=list)
    chn1_lin3: List[str] = field(default_factory=list)

    chn2_lin1: List[str] = field(default_factory=list)
    chn2_lin2: List[str] = field(default_factory=list)
    chn2_lin3: List[str] = field(default_factory=list)

    chn3_lin1: List[str] = field(default_factory=list)
    chn3_lin2: List[str] = field(default_factory=list)
    chn3_lin3: List[str] = field(default_factory=list)

    fechas_sorteo: List[str] = field(default_factory=list)

    fecha_seleccionada: str = ""
    sorteo_seleccionado: str = ""

    premio_desc: str = ""
    pronto_basta: str = ""

    nums_sorteo: List[str] = field(default_factory=list)
    nums_sorteo_tipo: str = ""

    chn1_cnt: int = 0
    chn2_cnt: int = 0
    chn3_cnt: int = 0

    img_evento: str = ""
    img_publicidad: str = ""

    dbg_parse: Dict[str, str] = field(default_factory=dict)

    dbg_data: Dict[str, str] = field(default_factory=dict)

                                                                    # UTILIDADES

def reproducir_audio(ruta):
    pygame.mixer.init()
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()

def btn_estilo(txt: str, on_click=None):
    return ft.ElevatedButton(
        txt, on_click=on_click,
        bgcolor="#E6CFCF",      # mismo tono que Form1
        color="#5A2A2A",        # texto marrón/rojo oscuro
        height=34,   )

def fmt_fecha_aaaammdd_a_ddmmaaaa(fecha: str) -> str:
    if not fecha:
        return ""
    if len(fecha) != 8 or not fecha.isdigit():
        return fecha
    return f"{fecha[6:8]}.{fecha[4:6]}.{fecha[0:4]}"


def dividir_lista_numeros(cadena: str) -> List[str]:         # delimitado por
                                                             # "_:" "." "," " " o 2chrs
    if not cadena:
        return []

    txt = str(cadena).strip()

    if "_" in txt:                                                      #dlmt"_"
        return [x.strip().zfill(2) for x in txt.split("_") if x.strip()]

    if len(txt) % 2 == 0:                                                 #2chrs
        return [txt[i:i + 2] for i in range(0, len(txt), 2)]

    return [txt]

def dividir_lista_sorteo(cadena: str) -> List[str]:
    if not cadena:
        return []

    txt = str(cadena)

    return [x.strip().zfill(2) for x in txt.split() if x.strip()]

def partir_3_lineas(lista: List[str]) -> tuple[list[str], list[str], list[str]]:
    lin1 = lista[0:10]
    lin2 = lista[10:20]
    lin3 = lista[20:30]
    return lin1, lin2, lin3

                                                         #retornar Texto o vacio
def txt_or_vacio(valor: Optional[str]) -> str:
    return valor if valor else ""

                                                     #generar35aleatorios(01-90)
def generar_numeros_aleatorios_35() -> List[str]:
    nums = random.sample(range(1, 91), 35)
  # nums.sort()
    return [str(n).zfill(2) for n in nums]

def fecha_hoy_aaaammdd() -> str:
    return datetime.now().strftime("%Y%m%d")

def es_imagen_disponible(ruta_img: str) -> bool:
    if not ruta_img:
        return False

    txt = str(ruta_img).strip()

    if txt == "":
        return False

    if txt.lower().startswith(("http://", "https://")):
        return True

    return os.path.exists(txt)

def ruta_a_data_uri(ruta_img: str) -> str:
    if not ruta_img:
        return ""

    txt = str(ruta_img).strip()

    if txt == "":
        return ""

    if txt.lower().startswith(("http://", "https://", "data:")):
        return txt

    if not os.path.exists(txt):
        return ""

    try:
        mime, _ = mimetypes.guess_type(txt)
        if not mime:
            mime = "image/jpeg"

        with open(txt, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")

        return f"data:{mime};base64,{b64}"
    except Exception:
        return ""

def crear_control_imagen(ruta_img: str, width: int, height=None):
    src_img = ruta_a_data_uri(ruta_img)

    if not src_img:
        return None

    kwargs = {"src": src_img, "width": width}

    if height is not None:
        kwargs["height"] = height

    return ft.Image(**kwargs)

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

def validar_id_cupon(url_id: str):
    s_id = "".join(ch for ch in str(url_id or "") if ch.isdigit())

    if s_id == "":
        return False, "Id vacío", None

    if len(s_id) != 13:
        return False, f"Id inválido: largo {len(s_id)} (debe ser 13)", None

    s_evn = s_id[0:5]
    s_sec = s_id[5:11]
    s_dv1 = s_id[11]
    s_dv2 = s_id[12]

    dv1 = calc_mod10(s_evn + s_sec)
    dv2 = calc_mod10(str(dv1) + s_sec + s_evn)

    if str(dv1) != s_dv1:
        return False, f"DígVerific1 inválido: recib {s_dv1}, calcul {dv1}", None

    if str(dv2) != s_dv2:
        return False, f"DígVerific2 inválido: recib {s_dv2}, calcul {dv2}", None

    return True, "OK", (s_evn, s_sec, s_dv1, s_dv2)

def recuperar_data_por_id(url_id):
    try:
        if not url_id or len(url_id) != 13:
            return "", "ID inválido (largo)"

        evn = int(url_id[0:5])
        sec = int(url_id[5:11])
        dv1 = int(url_id[11])
        dv2 = int(url_id[12])

        s_evn = url_id[0:5]
        s_sec = url_id[5:11]

        calc_dv1 = calc_mod10(s_evn + s_sec)
        calc_dv2 = calc_mod10(str(calc_dv1) + s_sec + s_evn)

        if dv1 != calc_dv1:
            return "", f"Error DV1 (esperado {calc_dv1})"

        if dv2 != calc_dv2:
            return "", f"Error DV2 (esperado {calc_dv2})"

        cnx = sqlite3.connect(DB)
        cur = cnx.cursor()

        cur.execute("""
            SELECT INF_DTA
              FROM INF_URL
             WHERE INF_EVN = ? AND INF_SEC = ?
        """, (evn, sec))

        row = cur.fetchone()
        cnx.close()

        if not row:
            return "", f"No existe registro EVN={evn} SEC={sec}"

        return row[0], ""

    except Exception as e:
        return "", f"Error: {e}"

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

def recuperar_valor(nombre_campo: str, valor_convertido: str) -> str:
    campos_numericos = { "EVNC_NUM", "EVNC_SEC",
        "EVNC_DES",  "EVNC_HAS",  "EVNC_GRP",  "EVNC_SUB", "MTZ_NUM",
        "CAR_SER",   "CAR_NUM",   "EVNC_SUB1", "MTZ_NUM1", "CAR_SER1",
        "CAR_NUM1",  "EVNC_SUB2", "MTZ_NUM2",  "CAR_SER2", "CAR_NUM2",
        "EVNC_SUB3", "MTZ_NUM3",  "CAR_SER3",  "CAR_NUM3",            }

    if nombre_campo in campos_numericos:
        return recuperar_numero(valor_convertido)

    return transformar_texto(valor_convertido)

ORDEN_DATA = [ "EVNC_NUM", "EVNC_SEC",
    "EVNC_DES", "EVNC_HAS", "EVNC_GRP", "EVNC_TPO", "EVNC_EST",
    "EVNC_TID", "EVNC_NID", "EVNC_NOM", "EVNC_UBI", "EVNC_DOM",
    "EVNC_REF", "EVNC_SOC", "EVNC_TRN", "EVNC_VEN", "EVNC_SUB",
    "MTZ_NUM",  "CAR_SER",  "CAR_NUM",  "CAR_LIS",  "EVNC_SUB1",
    "MTZ_NUM1", "CAR_SER1", "CAR_NUM1", "CAR_LIS1", "EVNC_SUB2",
    "MTZ_NUM2", "CAR_SER2", "CAR_NUM2", "CAR_LIS2", "EVNC_SUB3",
    "MTZ_NUM3", "CAR_SER3", "CAR_NUM3", "CAR_LIS3",             ]

                                                                        # PARSEO

def cargar_ctx_QueryString(ctx: CtxCupon, page: ft.Page) -> None:
    """
    Espera algo como:
        ?data=....
        ?id=123...
        ?fecha=20260115
        ?sorteo=0001
    """
    ctx.raw_url_data = ""
    ctx.url_id = ""
    ctx.msg_error = ""
    ctx.fecha_seleccionada = ""
    ctx.sorteo_seleccionado = ""
    ctx.dbg_url = {}

    wRoute = ""
    wUrl   = ""

    try:
        wRoute = str(page.route or "").strip()
    except Exception:
        wRoute = ""

    try:
        wUrl = str(page.url or "").strip()
    except Exception:
        wUrl = ""


    if wRoute != "":
        try:
            d_qs = parse_qs(urlparse(wRoute).query)
            ctx.raw_url_data = d_qs.get("data", [""])[0]
            ctx.url_id = d_qs.get("id", [""])[0]
            ctx.fecha_seleccionada = d_qs.get("fecha", [""])[0]
            ctx.sorteo_seleccionado = d_qs.get("sorteo", [""])[0]
        except Exception as exc:
            print("DBG error parse page.route:", exc)

    if ctx.raw_url_data == "" and ctx.url_id == "":
        try:
            d_qs = parse_qs(urlparse(wUrl).query)
            ctx.raw_url_data = d_qs.get("data", [""])[0]
            ctx.url_id = d_qs.get("id", [""])[0]
            ctx.fecha_seleccionada = d_qs.get("fecha", [""])[0]
            ctx.sorteo_seleccionado = d_qs.get("sorteo", [""])[0]
        except Exception as exc:
            print("DBG error parse page.url:", exc)

    ctx.dbg_url = { "PAGE_ROUTE": wRoute,
                    "PAGE_URL": wUrl,
                    "URL_ID": ctx.url_id,
                    "RAW_DATA_INICIAL": ctx.raw_url_data,
                    "FECHA": ctx.fecha_seleccionada,
                    "SORTEO": ctx.sorteo_seleccionado,   }

def parsear_data_principal(ctx: CtxCupon) -> None:
    if not ctx.raw_url_data and ctx.url_id:
        data, error = recuperar_data_por_id(ctx.url_id)

        if error:
            ctx.msg_error = error
            ctx.raw_url_data = ""
        else:
            ctx.raw_url_data = data

    ctx.cnx = None
    ctx.crs = None
    ctx.crs2 = None
    ctx.dbg_data = {}

    try:
        ctx.cnx = sqlite3.connect(r"D:\Python\Data\BYL\GES_BYL.DB")
        ctx.crs = ctx.cnx.cursor()
        ctx.crs2 = ctx.cnx.cursor()
    except Exception:
        ctx.cnx = None
        ctx.crs = None
        ctx.crs2 = None

  # print("DBG raw_url_data antes decode:", ctx.raw_url_data)

    if not ctx.raw_url_data:
        if ctx.msg_error == "":
            if ctx.url_id:
                ctx.msg_error = "No se pudo recuperar data desde INF_URL"
            else:
                ctx.msg_error = "URL vacía: no llegó ni data ni id"
        return

    txt_data = unquote(str(ctx.raw_url_data or "").strip())
  # print("DBG txt_data decode:", txt_data)

    valores = txt_data.split("~")
  # print("DBG cantidad valores:", len(valores))
  # print("DBG valores:", valores)

    if len(valores) < len(ORDEN_DATA):
        valores.extend([""] * (len(ORDEN_DATA) - len(valores)))

    d_data = {}

    for nom, val in zip(ORDEN_DATA, valores):
        d_data[nom] = recuperar_valor(nom, val)

    ctx.dbg_data = dict(d_data)

    ctx.evento       = txt_or_vacio(d_data.get("EVNC_NUM"))
    ctx.secuencia    = txt_or_vacio(d_data.get("EVNC_SEC"))
    ctx.vig_desde    = txt_or_vacio(d_data.get("EVNC_DES"))
    ctx.vig_hasta    = txt_or_vacio(d_data.get("EVNC_HAS"))
    ctx.tpoIdentidad = txt_or_vacio(d_data.get("EVNC_TID"))
    ctx.nroIdentidad = txt_or_vacio(d_data.get("EVNC_NID"))
    ctx.nombre       = txt_or_vacio(d_data.get("EVNC_NOM"))
    ctx.localidad    = txt_or_vacio(d_data.get("EVNC_UBI"))
    ctx.domicilio    = txt_or_vacio(d_data.get("EVNC_DOM"))
    ctx.referencia   = txt_or_vacio(d_data.get("EVNC_REF"))
    ctx.socioVinc    = txt_or_vacio(d_data.get("EVNC_SOC"))
    ctx.vendedor     = txt_or_vacio(d_data.get("EVNC_VEN"))

    def cargar_chance(num_chance: int) -> None:
        subsec = txt_or_vacio(d_data.get(f"EVNC_SUB{num_chance}"))
        mtz    = txt_or_vacio(d_data.get(f"MTZ_NUM{num_chance}"))
        serie  = txt_or_vacio(d_data.get(f"CAR_SER{num_chance}"))
        num    = txt_or_vacio(d_data.get(f"CAR_NUM{num_chance}"))
        lisnum = txt_or_vacio(d_data.get(f"CAR_LIS{num_chance}"))

        refcmb = ""

        if mtz or serie or num:
            refcmb = f"{mtz.zfill(2)}-{serie.zfill(6)}-{num}"

      # print(
      #     f"DBG chance{num_chance}: "
      #     f"subsec={subsec} mtz={mtz} serie={serie} num={num} lis={lisnum}" )

        setattr(ctx, f"subsec{num_chance}", subsec)
        setattr(ctx, f"refcmb{num_chance}", refcmb)
        setattr(ctx, f"lisnum{num_chance}", lisnum)

    cargar_chance(1)
    cargar_chance(2)
    cargar_chance(3)

                                                     # DATOS / BD (MOCK INICIAL)
def recuperar_imagen_evento(ctx: CtxCupon) -> None:
    ruta01  = rf"D:\Python\PreFmt\BYL\Evn{ctx.evento}_01.jpeg"
    ruta02a = rf"D:\Python\PreFmt\BYL\Evn{ctx.evento}_02a.jpeg"
    ruta02b = rf"D:\Python\PreFmt\BYL\Evn{ctx.evento}_02b.jpeg"

    if os.path.exists(ruta02a):
        ctx.img_evento = ruta02a
    elif os.path.exists(ruta01):
        ctx.img_evento = ruta01
    else:
        ctx.img_evento = ""

    if os.path.exists(ruta02b):
        ctx.img_publicidad = ruta02b
    else:
        ctx.img_publicidad = ""

def recuperar_fechas_sorteo(ctx: CtxCupon) -> None:

    if not ctx.vig_desde or not ctx.vig_hasta:
        ctx.fechas_sorteo = []
        return

    wStmSql = """SELECT Srt_Fcha
                   FROM SrtFechas A
                  WHERE Evn_Num = ? And Srt_Fcha Between ? And ?
                  ORDER BY Srt_Fcha """

    if ctx.crs:
        try:
            ctx.crs.execute(wStmSql, (ctx.evento, ctx.vig_desde, ctx.vig_hasta))
            rows = ctx.crs.fetchall()
            ctx.fechas_sorteo = [ str(row[0]) for row in rows if row[0] ]
            if ctx.fechas_sorteo:
                return
        except Exception:
            pass

def recuperar_sorteos_de_fecha(ctx: CtxCupon, fecha: str) -> List[Dict[str, str]]:

    sorteos = []

    wStmSql = """SELECT A.SRT_NRO, B.SRT_NUM, B.SRT_PRE1, B.SRT_PRE2
                   FROM SrtFchNum A
                   LEFT JOIN SORTEOS B
                     ON B.EVN_NUM = A.EVN_NUM AND B.SRT_NUM = A.SRT_RELA
                  WHERE A.EVN_NUM = ? AND A.SRT_FCHA = ?
                  ORDER BY A.EVN_NUM, A.SRT_FCHA, A.SRT_NRO """
    if ctx.crs:
        try:
            ctx.crs.execute(wStmSql, (ctx.evento, fecha))
            rows = ctx.crs.fetchall()

            for row in rows:
                sorteos.append( { "SrtNum":  str(row[0] or ""),
                                  "SrtPre1": str(row[2] or ""),
                                  "SrtPre2": str(row[3] or ""), } )
            return sorteos

        except Exception as exc:
            print("Error recuperar_sorteos_de_fecha:", exc)

    return []

def recuperar_detalle_sorteo(
    ctx: CtxCupon, fecha: str, num_sorteo: str ) -> Dict[str, object]:

    nums, srt_pre1, srt_pre2, tipo = [], "", "", "Números Simulados"

    wStmSql = """SELECT A.SRT_NRO,  B.SRT_PRE1, B.SRT_PRE2, B.SRT_COL1,
                        B.SRT_COL2, B.SRT_COL3, B.SRT_COL4, B.SRT_COL5,
                        B.SRT_COL6
                   FROM SrtFchNum A
                   LEFT JOIN SORTEOS B
                     ON B.EVN_NUM = A.EVN_NUM AND B.SRT_NUM = A.SRT_RELA
                  WHERE A.EVN_NUM = ? AND A.SRT_FCHA = ?
                    AND A.SRT_NRO = ?
                  ORDER BY A.EVN_NUM, A.SRT_FCHA, A.SRT_NRO """
    if ctx.crs:
        try:
            ctx.crs.execute(wStmSql, (ctx.evento, fecha, num_sorteo))
            row = ctx.crs.fetchone()
            if row:
                srt_pre1 = str(row[1] or "")
                srt_pre2 = str(row[2] or "")
                cadena_nums = ( str(row[3] or "") +
                    str(row[4] or "") + str(row[5] or "") +
                    str(row[6] or "") + str(row[7] or "") +
                    str(row[8] or "")                    )
                if cadena_nums.strip() != "":
                    nums = dividir_lista_sorteo(cadena_nums)
                    tipo = "Números Reales"
                else:
                    nums = generar_numeros_aleatorios_35()
                    tipo = "Números Simulados"
        except Exception as exc:
            print("Error recuperar_detalle_sorteo:", exc)
    if not nums:
        nums = generar_numeros_aleatorios_35()
        tipo = "Números Simulados"

    return { "SrtNum":  str(num_sorteo), "SrtPre1": str(srt_pre1),
             "SrtPre2": str(srt_pre2),   "Nums":    nums,
             "Tipo":    tipo,                                     }

def recuperar_textos_ayuda(ctx: CtxCupon, codi: str) -> List[str]:

    if ctx.crs2:
        try:
            wStmSql = """SELECT HLPD_TEXT
                           FROM HLP_TXT
                          WHERE HLPD_CODI = ?
                          ORDER BY HLPD_SECU """
            ctx.crs2.execute(wStmSql, (codi,))
            rows = ctx.crs2.fetchall()
            textos = [ str(row[0]) for row in rows if row and row[0] ]
            if textos:
                return textos
        except Exception:
            pass
        try:
            wStmSql = """SELECT HLPD_DSCR
                           FROM HLP_TXT
                          WHERE HLPD_CODI = ?
                          ORDER BY HLPD_SECU """
            ctx.crs2.execute(wStmSql, (codi,))
            rows = ctx.crs2.fetchall()
            textos = [ str(row[0]) for row in rows if row and row[0] ]
            if textos:
                return textos
        except Exception:
            pass

    if codi == "SOMOS":
        return [
            "ABG Servicios Informáticos es una empresa especializada en la automatización de procesos informáticos,",
            "con más de 40 años de trayectoria, brindando soluciones a la industria azucarera, al comercio en general",
            "y al sector financiero en particular.___________________________________________________________________", ]

    if codi == "HELP1":
        return [
            "El visor de Cupones Digitales de Bingo ABG, es una Aplicacion que permite visualizar los distintos",
            "cartones de un juego de Bingo, con posibilidad de ver los premios habilitados en el rango de la ",
            "vigencia del cupon, con posibilidad de controlar la cantidad de numeros anotado con los numeros de",
            "un sorteo ya realizado o con numeros aleatorios (supuestos) para un sorteo futuro.________________", ]

    return ["No hay información disponible."]

def recuperar_publicaciones(ctx: CtxCupon) -> List[Dict[str, str]]:

    if not ctx.cnx:
        print("PUB_DEF: sin conexion")
        return []

    wFechaCtl = fecha_hoy_aaaammdd()
    wEvento   = txt_or_vacio(ctx.evento).strip()

    wStmSql = """SELECT PUBC_CODI, PUBC_DSCR, PUBC_IMAG, PUBC_ENLC
                   FROM PUB_DEF
                  WHERE PUBC_EVN = ? AND PUBC_ESTD = ?
                    AND ? BETWEEN PUBC_VIG1 AND PUBC_VIG2
                  ORDER BY PUBC_ORDN, PUBC_CODI """
    try:
        crs_pub = ctx.cnx.cursor()
        crs_pub.execute(wStmSql, (wEvento, "A", wFechaCtl))
        rows = crs_pub.fetchall()

        return [ { "PUBC_CODI": txt_or_vacio(row[0]),
                   "PUBC_DSCR": txt_or_vacio(row[1]),
                   "PUBC_IMAG": txt_or_vacio(row[2]),
                   "PUBC_ENLC": txt_or_vacio(row[3]), }
            for row in rows                             ]

    except Exception as exc:
        print("Error al leer PUB_DEF:", exc)
        print("SQL PUB_DEF:", wStmSql)
        print("PARM PUB_DEF:", (wEvento, "V", wFechaCtl))
        return []

                                                             # PROCESO PRINCIPAL

def procesar_formulario1(ctx: CtxCupon) -> None:
    recuperar_imagen_evento(ctx)
    recuperar_fechas_sorteo(ctx)

    lis1 = dividir_lista_numeros(ctx.lisnum1)
    lis2 = dividir_lista_numeros(ctx.lisnum2)
    lis3 = dividir_lista_numeros(ctx.lisnum3)

  # print(f"DBG parse chance1 raw={ctx.lisnum1}")
  # print(f"DBG parse chance1 len={len(lis1)} vals={lis1}")
  # print(f"DBG parse chance2 raw={ctx.lisnum2}")
  # print(f"DBG parse chance2 len={len(lis2)} vals={lis2}")
  # print(f"DBG parse chance3 raw={ctx.lisnum3}")
  # print(f"DBG parse chance3 len={len(lis3)} vals={lis3}")

    ctx.dbg_parse = { "CH1_RAW": txt_or_vacio(ctx.lisnum1),
                      "CH1_LEN": str(len(lis1)),
                      "CH1_VALS": " ~ ".join(lis1),
                      "CH2_RAW": txt_or_vacio(ctx.lisnum2),
                      "CH2_LEN": str(len(lis2)),
                      "CH2_VALS": " ~ ".join(lis2),
                      "CH3_RAW": txt_or_vacio(ctx.lisnum3),
                      "CH3_LEN": str(len(lis3)),
                      "CH3_VALS": " ~ ".join(lis3),         }

    ctx.chn1_lin1, ctx.chn1_lin2, ctx.chn1_lin3 = partir_3_lineas(lis1)
    ctx.chn2_lin1, ctx.chn2_lin2, ctx.chn2_lin3 = partir_3_lineas(lis2)
    ctx.chn3_lin1, ctx.chn3_lin2, ctx.chn3_lin3 = partir_3_lineas(lis3)

def cnt_num_anotados_mock(lista_txt: str, nums_sorteo: List[str]) -> int:

    if not lista_txt:
        return 0

    lista = dividir_lista_numeros(lista_txt)
    s_sorteo = set(nums_sorteo)
    return sum(1 for x in lista if x in s_sorteo)

def procesar_formulario3( ctx: CtxCupon, fecha: str, num_sorteo: str ) -> None:

    det = recuperar_detalle_sorteo(ctx, fecha, num_sorteo)

    ctx.sorteo_seleccionado = str(det.get("SrtNum", ""))
    ctx.premio_desc = str(det.get("SrtPre1", ""))
    ctx.pronto_basta = str(det.get("SrtPre2", ""))
    ctx.nums_sorteo = list(det.get("Nums", []))
    ctx.nums_sorteo_tipo = str(det.get("Tipo", ""))

    ctx.chn1_cnt = cnt_num_anotados_mock(ctx.lisnum1, ctx.nums_sorteo)
    ctx.chn2_cnt = cnt_num_anotados_mock(ctx.lisnum2, ctx.nums_sorteo)
    ctx.chn3_cnt = cnt_num_anotados_mock(ctx.lisnum3, ctx.nums_sorteo)

                                                                            # UI
def bloque_campo(etiqueta: str, valor: str, ancho_label: int = 130) -> ft.Row:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(etiqueta, weight=ft.FontWeight.BOLD),
                width=ancho_label,                                   ),
            ft.Container(
                content=ft.Text(valor, selectable=True),
                expand=True,                                         ), ],
        spacing=3,                                                        )

def fila_numeros(lista: List[str]) -> ft.Row:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(x, text_align=ft.TextAlign.CENTER),
                width=32, height=26,
                border=ft.border.all(1, "#D7B5B5"),
                border_radius=4, bgcolor="#FBF5F4",                )
            for x in lista                                          ],
        spacing=4, wrap=False,                                       )

def bloque_chance( titulo: str, subsec: str, refcmb: str,
                   lin1: List[str], lin2: List[str], lin3: List[str],
                  ) -> ft.Container:

    ancho_label = 75                                                 # antes 90

    fila1 = ft.Row(
        controls=[
            ft.Container( content=ft.Text(f"{titulo}   ",
                                          weight=ft.FontWeight.BOLD ),
                          width=ancho_label                           ),
            ft.Container( content=fila_numeros(lin1),
                          margin=ft.margin.only(left=10) ), ],
        spacing=2,                                                     )

    fila2 = ft.Row(
        controls=[
            ft.Container( content=ft.Text(f"{subsec}  {refcmb}", size=10),
                          width=ancho_label                               ),
            ft.Container( content=fila_numeros(lin2),
                          margin=ft.margin.only(left=10)                  ), ],
        spacing=2,                                  )

    fila3 = ft.Row(
        controls=[
            ft.Container(width=ancho_label),
            ft.Container( content=fila_numeros(lin3),
                          margin=ft.margin.only(left=10) ), ],
        spacing=2,                                            )

    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[fila1, fila2, fila3],
                    spacing=0,                     ),
                padding=ft.padding.only(top=2, bottom=1, left=6, right=6),
                border=ft.border.all(1, "#D7B5B5"),
                bgcolor="#F8F2F2",
                border_radius=8,
                margin=ft.margin.only(bottom=2),                          ) ],
        spacing=0,                                                             )

def construir_grilla_35(nums: List[str]) -> ft.Column:
    filas = []
    for i in range(0, len(nums), 10):
        filas.append(fila_numeros(nums[i:i + 10]))
    return ft.Column(controls=filas, spacing=6)

def bloque_debug_diccionario(ctx: CtxCupon) -> ft.Container:
    lineas = []

    if ctx.dbg_data:
        for clave, valor in ctx.dbg_data.items():
            lineas.append(
                ft.Text(
                    f"{clave} = {txt_or_vacio(valor)}",
                    selectable=True, size=12,          ) )

    if ctx.dbg_parse:
        if lineas:
            lineas.append(ft.Container(height=8))
        lineas.append(
            ft.Text( "Debug parseo chances", size=14,
                     weight=ft.FontWeight.BOLD, color="#6A1B1B", ) )
        for clave, valor in ctx.dbg_parse.items():
            lineas.append(
                ft.Text( f"{clave} = {txt_or_vacio(valor)}",
                         selectable=True, size=12,           ) )

    if not lineas:
        lineas.append(ft.Text("Sin datos de depuración.", size=12))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text( "Debug diccionario", size=16,
                         weight=ft.FontWeight.BOLD, color="#6A1B1B", ),
                ft.Column( controls=lineas, spacing=2,
                           scroll=ft.ScrollMode.AUTO, height=340,    ), ],
            spacing=6,                                          ),
        padding=10, border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8, bgcolor="#F8F2F2",                       )


def bloque_error_url(ctx: CtxCupon) -> Optional[ft.Container]:
    if txt_or_vacio(ctx.msg_error) == "" and not ctx.dbg_url:
        return None

    lineas = []

    if txt_or_vacio(ctx.msg_error) != "":
        lineas.append(
            ft.Text( f"Error: {ctx.msg_error}",
                     color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD,
                     selectable=True,                                   ) )

    for clave, valor in ctx.dbg_url.items():
        lineas.append(
            ft.Text( f"{clave} = {txt_or_vacio(valor)}",
                     selectable=True, size=12,          ) )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text( "Debug URL / ID", size=16,
                         weight=ft.FontWeight.BOLD, color="#6A1B1B", ),
                ft.Column( controls=lineas, spacing=2,
                           scroll=ft.ScrollMode.AUTO, height=180,    ), ],
            spacing=6,                                                    ),
        padding=10, border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=8, bgcolor="#F8F2F2",                              )

def texto_resultado_chance(nombre: str, cant_nums: int, anotados: int) -> str:
    if cant_nums <= 0:
        return ""

    if anotados == cant_nums:
        return f"{nombre}: ¡Ganaste!"

    if anotados == cant_nums - 1:
        return f"{nombre}: ¡Te faltó muy poco para ganar!"

    if anotados == 0:
        return f"{nombre}: ¡Tienes nueva chance en el sorteo especial!"

    return ""

                                                                     # MAIN FLET
def main(page: ft.Page) -> None:
    page.title = "Visor de Cupones"
    page.window_width = 420
    page.window_height = 900
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#F3E9E6"

    ctx = CtxCupon()

    cargar_ctx_QueryString(ctx, page)
    parsear_data_principal(ctx)
    procesar_formulario1(ctx)

    historial = ["form1"]

    body = ft.Container(expand=True, padding=0)
    page.add(body)

    def mostrar(control) -> None:
        body.content = control
        page.update()

    def volver() -> None:
        if len(historial) <= 1:
            return

        historial.pop()
        destino = historial[-1]

        if destino == "form1":
            _mostrar_formulario1(registrar=False)
        elif destino == "form2":
            _mostrar_formulario2(ctx.fecha_seleccionada, registrar=False)
        elif destino == "form3":
            _mostrar_formulario3(ctx.fecha_seleccionada,
                                 ctx.sorteo_seleccionado, registrar=False)
        elif destino == "form4":
            _mostrar_formulario4(registrar=False)
        elif destino == "abg":
            _mostrar_ayuda("SOMOS", "ABG", registrar=False)
        elif destino == "ayuda":
            _mostrar_ayuda("HELP1", "AYUDA", registrar=False)

  # async def cerrar_app(e) -> None:                         #xllamarDesdeWindow
  #     await page.window.close()

    def cerrar_app(e) -> None:                               #xllamadaWeb
        mostrar(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text( "Puede cerrar esta pestaña.", size=22,
                            weight=ft.FontWeight.BOLD,                  ),
                        ft.Text(
                            "Los navegadores no permiten cerrar automáticamente "
                            "una pestaña abierta por el usuario.",
                            size=16,                                             ), ],
                    spacing=10,                                                       ),
                padding=20,                                                             ) )

    def _mostrar_ayuda(codi: str, titulo: str,
                       registrar: bool = True) -> None:
        if registrar:
            if codi == "SOMOS":
                historial.append("abg")
            else:
                historial.append("ayuda")

        textos = recuperar_textos_ayuda(ctx, codi)

        controles = [ ft.Text( titulo, size=22,
                               weight=ft.FontWeight.BOLD, ), ]

        for txt1 in textos:
            controles.append( ft.Text(txt1, selectable=True) )

        controles.append(
            btn_estilo( "Volver", on_click=lambda e: volver(), ) )

        mostrar(
            ft.Container(
                content=ft.Container(             # 👈contenedorInternoConBorde
                    content=ft.Column(
                        controls=controles, spacing=6,
                        scroll=ft.ScrollMode.AUTO, expand=True, ),
                    padding=10, border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=8,                                        ),
                padding=ft.padding.only(left=15, right=15),                   ) )

    def _crear_control_publicacion(pub: Dict[str, str]):

        wDscr = txt_or_vacio(pub.get("PUBC_DSCR"))
        wImg  = txt_or_vacio(pub.get("PUBC_IMAG"))   # ✔ correcto
        wUrl  = txt_or_vacio(pub.get("PUBC_ENLC"))   # ✔ correcto

        def abrir_publicacion(e) -> None:
            if wUrl:
                import webbrowser
                webbrowser.open(wUrl)

        if es_imagen_disponible(wImg):
            img_ctl = crear_control_imagen(wImg, width=120, height=46)

            if img_ctl is not None:
                return ft.Container(
                    content=img_ctl,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=8,
                    padding=ft.padding.all(4),
                    tooltip=wDscr if wDscr else wUrl,
                    on_click=abrir_publicacion,                      )

        return ft.ElevatedButton(
            wDscr if wDscr else "Publicación",
            tooltip=wUrl if wUrl else None,
            on_click=abrir_publicacion,
            bgcolor="#E8CFCF", color="#5A2A2A", )

    def _bloque_publicaciones() -> Optional[ft.Container]:
        publicaciones = recuperar_publicaciones(ctx)

        if not publicaciones:
            return None

        controles = [ _crear_control_publicacion(pub)
                      for pub in publicaciones ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text( "Publicaciones", size=18,
                             weight=ft.FontWeight.BOLD,
                             color="#6A1B1B", ),
                    ft.Column( controls=controles, spacing=8, ), ],
                spacing=6,                                         ),
            padding=ft.padding.only(left=15, right=15, bottom=20),   )

    def _mostrar_formulario4(registrar: bool = True) -> None:
        if registrar:
            historial.append("form4")

        controles = [
            ft.Text( "Datos", size=22,
                     weight=ft.FontWeight.BOLD, ),

            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text( f"Secuencia: {str(ctx.secuencia).zfill(6)}",
                                         weight=ft.FontWeight.BOLD, ),
                                ft.Text(
                                    f"Vigencia: "
                                    f"{fmt_fecha_aaaammdd_a_ddmmaaaa(ctx.vig_desde)}"
                                    f"  al  "
                                    f"{fmt_fecha_aaaammdd_a_ddmmaaaa(ctx.vig_hasta)}",
                                    weight=ft.FontWeight.BOLD, ),                     ],
                            spacing=30, wrap=True,                                      ),

                        bloque_campo( "Socio / Vendedor",
                                      f"S:{ctx.socioVinc} - V:{ctx.vendedor}" ),
                        bloque_campo( "Identidad",
                                      f"{ctx.tpoIdentidad} {ctx.nroIdentidad}" ),
                        bloque_campo( "Nombre", ctx.nombre ),
                        bloque_campo( "Domicilio", ctx.domicilio ),
                        bloque_campo( "Localidad", ctx.localidad ),
                        bloque_campo( "Referencia", ctx.referencia ),                 ],
                    spacing=4,                                                          ),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=8, width=500,                                               ),

          # bloque_debug_diccionario(ctx),

            btn_estilo( "Volver",
                               on_click=lambda e: volver(), ),                              ]

        mostrar(
            ft.Container(
                content=ft.Column(
                    controls=controles, spacing=8,
                    scroll=ft.ScrollMode.AUTO, expand=True, ),
                padding=ft.padding.only(left=15, right=15), ) )

    def _mostrar_formulario1(registrar: bool = True) -> None:
        if registrar:
            historial.append("form1")

        bloques = []

        if ctx.img_evento:
            img_ctl = crear_control_imagen(ctx.img_evento, width=460)

            if img_ctl is not None:
                bloques.append(
                    ft.Container(
                        content=img_ctl,                                 # 410, height=190,
                        padding=ft.padding.only(left=15, top=6, bottom=4),
                        margin=0,                                           ) )

        bloques.append(
            ft.Container(
                content=ft.Text( "Cupón Digital", size=22,
                                 weight=ft.FontWeight.BOLD,
                                 color="#6A1B1B",  ),
                padding=ft.padding.only(left=155, right=15),    ) )

        bloques.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text( f"Secuencia: {str(ctx.secuencia).zfill(6)}",
                                 weight=ft.FontWeight.BOLD, ),
                        ft.Text(
                            f"Vigencia: "
                            f"{fmt_fecha_aaaammdd_a_ddmmaaaa(ctx.vig_desde)}"
                            f"  al  "
                            f"{fmt_fecha_aaaammdd_a_ddmmaaaa(ctx.vig_hasta)}",
                            weight=ft.FontWeight.BOLD, ),                     ],
                    spacing=30, wrap=True,                                      ),
                padding=ft.padding.only(left=15, right=15), ) )

        if str(ctx.lisnum1).strip():
            bloques.append( ft.Container( content=bloque_chance( "Chance 1", ctx.subsec1,
                               ctx.refcmb1, ctx.chn1_lin1, ctx.chn1_lin2,
                               ctx.chn1_lin3, ),
                               padding=ft.padding.only(left=15, right=15), ) )

        if str(ctx.lisnum2).strip():
            bloques.append( ft.Container( content=bloque_chance( "Chance 2", ctx.subsec2,
                               ctx.refcmb2, ctx.chn2_lin1, ctx.chn2_lin2,
                               ctx.chn2_lin3, ),
                               padding=ft.padding.only(left=15, right=15), ) )

        if str(ctx.lisnum3).strip():
            bloques.append( ft.Container( content=bloque_chance( "Chance 3", ctx.subsec3,
                               ctx.refcmb3, ctx.chn3_lin1, ctx.chn3_lin2,
                               ctx.chn3_lin3, ),
                               padding=ft.padding.only(left=15, right=15), ) )

        bloques.append( ft.Container( content=ft.Text( "Fechas de los Sorteos", size=18,
                                 weight=ft.FontWeight.BOLD,
                                 color="#6A1B1B", ),
                                       padding=ft.padding.only(left=15, right=15), ) )

        botones_fechas = []

        for fecha in ctx.fechas_sorteo:
            botones_fechas.append(
                ft.ElevatedButton(
                    content=ft.Text(
                        fmt_fecha_aaaammdd_a_ddmmaaaa(fecha), size=11,
                        weight=ft.FontWeight.BOLD,                    ),
                    on_click=lambda e, f=fecha: _mostrar_formulario2(f),
                    bgcolor="#C62828", color="white", height=20, ) )

        bloques.append(
            ft.Container(
                content=ft.Row(
                    controls=botones_fechas, spacing=12, wrap=False, ),
                padding=ft.padding.only(left=5, right=5), ) )

        bloques.append( ft.Container(height=14) )

        bloques.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.ElevatedButton("Datos",
                            on_click=lambda e: _mostrar_formulario4(),
                            bgcolor="#E8CFCF", color="#5A2A2A"        ),
                        ft.ElevatedButton("ABG",
                            on_click=lambda e: _mostrar_ayuda("SOMOS", "ABG"),
                            bgcolor="#E8CFCF", color="#5A2A2A"                ),
                        ft.ElevatedButton("Ayuda",
                            on_click=lambda e: _mostrar_ayuda("HELP1", "AYUDA"),
                            bgcolor="#E8CFCF", color="#5A2A2A"                  ),
                        ft.ElevatedButton("Finalizar",
                            on_click=cerrar_app,
                            bgcolor="#E8CFCF", color="#5A2A2A"                  ), ],
                    spacing=10, wrap=True,                                           ),
                padding=ft.padding.only(left=15, right=15),
                margin=ft.margin.only(bottom=20),                                     ) )

        bloque_pub = _bloque_publicaciones()
        if bloque_pub is not None:
            bloques.append(bloque_pub)

        if ctx.img_publicidad:
            img_ctl = crear_control_imagen(ctx.img_publicidad, width=460)

            if img_ctl is not None:
                bloques.append(
                    ft.Container(
                        content=img_ctl,
                        padding=ft.padding.only(left=15, right=15, bottom=20), ) )

        mostrar( ft.Column( controls=bloques, spacing=4,
                            scroll=ft.ScrollMode.AUTO, expand=True, ) )

    def _mostrar_formulario2(fecha: str, registrar: bool = True) -> None:
        if registrar:
            historial.append("form2")

        ctx.fecha_seleccionada = fecha
        sorteos = recuperar_sorteos_de_fecha(ctx, fecha)

        controles = [
            ft.Text( "Premios", size=22,
                     weight=ft.FontWeight.BOLD, ),
            ft.Text( f"Fecha: {fmt_fecha_aaaammdd_a_ddmmaaaa(fecha)}",
                     size=16, weight=ft.FontWeight.BOLD, ),           ]

        for reg in sorteos:
            srt_num  = reg.get("SrtNum",  "")
            srt_pre1 = reg.get("SrtPre1", "")
            srt_pre2 = reg.get("SrtPre2", "")

            controles.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=470,
                            content=ft.Column(
                                controls=[
                                    ft.Text( f"Sorteo: {srt_num}   "
                                             f"Premio: {srt_pre1}",
                                             weight=ft.FontWeight.BOLD, ),
                                    ft.Text( f"Pronto: {srt_pre2}" ),
                                    ft.Row(
                                        controls=[
                                            btn_estilo( "Ver",
                                                on_click=lambda e, n=srt_num, f=fecha:
                                                    _mostrar_formulario3(f, n),       ) , ], ), ],
                                spacing=6, ),
                            padding=10,
                            border=ft.border.all(1, ft.Colors.GREY_400),
                            border_radius=8, ) ],
                    spacing=0, ) )

        controles.append(
            btn_estilo( "Volver", on_click=lambda e: volver(), ) )

        mostrar(
            ft.Container(
                content=ft.Column( controls=controles, spacing=12,
                                   scroll=ft.ScrollMode.AUTO, expand=True, ),
                                   padding=ft.padding.only(left=15, right=15), ) )

    def _mostrar_formulario3( fecha: str, sorteo: str, registrar: bool = True,
                             ) -> None:
        if registrar:
            historial.append("form3")

        ctx.fecha_seleccionada = fecha
        ctx.sorteo_seleccionado = sorteo
        procesar_formulario3(ctx, fecha, sorteo)

        controles = [
            ft.Text( "Controles", size=22,
                     weight=ft.FontWeight.BOLD, ),

            ft.Text( f"Fecha: {fmt_fecha_aaaammdd_a_ddmmaaaa(fecha)}",
                     size=16, weight=ft.FontWeight.BOLD, ),

            ft.Text( f"Sorteo: {ctx.sorteo_seleccionado}   "
                     f"Premio: {ctx.premio_desc}",
                     weight=ft.FontWeight.BOLD, ),

            ft.Row( controls=[
                        ft.Container(width=74),
                        ft.Text( f"Pronto: {ctx.pronto_basta}",
                                 weight=ft.FontWeight.BOLD, ), ],
                    spacing=0,                                   ), ]

                                                                       # Chances
        controles.append(
            ft.Text("Chances:", weight=ft.FontWeight.BOLD) )

        controles.append(
            ft.Row(
                controls=[
                    ft.Text("1:", width=24),
                    fila_numeros(ctx.chn1_lin1 + ctx.chn1_lin2 + ctx.chn1_lin3), ],
                spacing=6,                                                         ) )

        controles.append(
            ft.Row(
                controls=[
                    ft.Text("2:", width=24),
                    fila_numeros(ctx.chn2_lin1 + ctx.chn2_lin2 + ctx.chn2_lin3), ],
                spacing=6,                                                         ) )

        if ctx.chn3_lin1 or ctx.chn3_lin2 or ctx.chn3_lin3:
            controles.append(
                ft.Row(
                    controls=[
                        ft.Text("3:", width=24),
                        fila_numeros(ctx.chn3_lin1 + ctx.chn3_lin2 + ctx.chn3_lin3), ],
                    spacing=6,                                                         ) )

                                                                # Numeros sorteo
        controles.append(
            ft.Text(f"{ctx.nums_sorteo_tipo}",
                     weight=ft.FontWeight.BOLD) )

        controles.append(
            ft.Row( controls=[
                       ft.Container(width=30),            # <-- ajusteAlineación
                       construir_grilla_35(ctx.nums_sorteo), ],
                    spacing=0,                                      ) )

      # controles.append(
      #     ft.Text( f"Anotados:   Chance1={ctx.chn1_cnt}   "
      #              f"Chance2={ctx.chn2_cnt}   "
      #              f"Chance3={ctx.chn3_cnt}",
      #              weight=ft.FontWeight.BOLD, ), )

        txt_anotados = f"Anotados:   Chance1={ctx.chn1_cnt}"

        if ctx.chn2_lin1 or ctx.chn2_lin2 or ctx.chn2_lin3:
            txt_anotados += f"   Chance2={ctx.chn2_cnt}"

        if ctx.chn3_lin1 or ctx.chn3_lin2 or ctx.chn3_lin3:
            txt_anotados += f"   Chance3={ctx.chn3_cnt}"

        controles.append(
            ft.Text(txt_anotados, weight=ft.FontWeight.BOLD) )

        mensajes = []

        cnt_ch1 = len(ctx.chn1_lin1 + ctx.chn1_lin2 + ctx.chn1_lin3)
        cnt_ch2 = len(ctx.chn2_lin1 + ctx.chn2_lin2 + ctx.chn2_lin3)
        cnt_ch3 = len(ctx.chn3_lin1 + ctx.chn3_lin2 + ctx.chn3_lin3)

        msg = texto_resultado_chance("Chance1", cnt_ch1, ctx.chn1_cnt)
        if msg:
            mensajes.append(msg)

        if cnt_ch2 > 0:
            msg = texto_resultado_chance("Chance2", cnt_ch2, ctx.chn2_cnt)
            if msg:
                mensajes.append(msg)

        if cnt_ch3 > 0:
            msg = texto_resultado_chance("Chance3", cnt_ch3, ctx.chn3_cnt)
            if msg:
                mensajes.append(msg)

        audio_a_reproducir = None
                                                            # PRIORIDAD: GANASTE
        if cnt_ch1 > 0 and ctx.chn1_cnt == cnt_ch1:
            audio_a_reproducir = "ganaste.mp3"
        elif cnt_ch2 > 0 and ctx.chn2_cnt == cnt_ch2:
            audio_a_reproducir = "ganaste.mp3"
        elif cnt_ch3 > 0 and ctx.chn3_cnt == cnt_ch3:
            audio_a_reproducir = "ganaste.mp3"
                                                        # PRIORIDAD 2: CASI CASI
        elif cnt_ch1 > 0 and ctx.chn1_cnt == cnt_ch1 - 1:
            audio_a_reproducir = "casicasi.mp3"
        elif cnt_ch2 > 0 and ctx.chn2_cnt == cnt_ch2 - 1:
            audio_a_reproducir = "casicasi.mp3"
        elif cnt_ch3 > 0 and ctx.chn3_cnt == cnt_ch3 - 1:
            audio_a_reproducir = "casicasi.mp3"

        if audio_a_reproducir:
            try:
                reproducir_audio(audio_a_reproducir)
            except Exception as e:
                print("Error audio:", e)

        for msg in mensajes:
            controles.append(
                ft.Text( msg, size=18, weight=ft.FontWeight.BOLD,
                         color="#C62828",                        ) )

        controles.append(
            ft.Row( controls=[ btn_estilo( "Volver",
                                  on_click=lambda e: volver(), ) ] ) )

        mostrar(
            ft.Container(
                content=ft.Column(
                    controls=controles, spacing=12,
                    scroll=ft.ScrollMode.AUTO, expand=True, ),
                padding=ft.padding.only(left=15, right=15), ) )

    _mostrar_formulario1(registrar=False)


#if __name__ == "__main__":                                     #xLlamadaWindows
#    ft.run(main)

if __name__ == "__main__":                                      #xLLamadaWeb
    ft.run( main, view=ft.AppView.WEB_BROWSER,
            host="0.0.0.0", port=8550,         )


# Operatoria previa
# D:
# cd D:\Python\Pgm\BYL
#                                         #asignaVariableEntorno-InvocarServicio
# set FLET_FORCE_WEB_SERVER=true
# python VisorCupones.py

#                                                  la app queda accesible desde:
# http://localhost:8550

#                                                                   o desde red:
# http://IP_DE_TU_PC:8550

                                                           # Cómo ejecutar:
                                                             # Desde consola:
# python VisorCupones.py
                                                             # con navegador a:
# http://127.0.0.1:8550                                        # alternativa1
# http://localhost:8550                                        # alternativa2

# ipconfig                                          # IPv4 Address: 192.168.0.25

# http://192.168.0.25:8550/?data=-