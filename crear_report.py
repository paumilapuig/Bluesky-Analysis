
"""
Script complet per generar automàticament el Bluesky Report utilitzant les teves funcions de creació i anàlisi de graf:
- Extracció de threads i dades de customer.bsky.social
- Construcció i anàlisi de graf amb funcions pròpies
- Creació de l'informe de text
- Generació de PDF únic amb fpdf2
"""


import os
import glob
from datetime import datetime
from fpdf import FPDF
from pathlib import Path
import graph_tool.all as gt
from segona_part.seguidors.f_influents_receptors import generar_influents_receptors
from segona_part.seguidors.f_comunitats import detectar_comunitats_model_blocs, retornar_estadistiques_comunitats, visualitzar_graf
from segona_part.seguidors.f_competidors import centralitat_proximitat, mostrar_resultats
from segona_part.seguidors.f_reputacio import calcular_top_reputacio
from segona_part.threads.punts_de_pas import generar_punts_de_pas
from segona_part.threads.vertexs_de_sortida import vertexs_de_sortida
from primera_part import crear_graf_seguidors, crear_graf_threads


# ------- 1. CONFIGURACIÓ DE CONSTANTS --------
CLIENT = input("Escriu el handle del usuari del qual vols crear el report: ")
DATE = datetime.now().strftime("%Y-%m-%d")
BASE = f"bluesky-report-{CLIENT}"
TXT_PATH = f"{BASE}.txt"
PDF_PATH = f"{BASE}.pdf"



# ------- 2. ELIMINACIÓ DE GRAFS REPETITS -------
def eliminar_grafs(tipo: str, client: str) -> None:
    """
    Elimina arxius .gt i .png de grafs per a un tipus ('seguidors' o 'threads')
    i també elimina els 'graf_comunitats' si el tipus és 'seguidors'.

    Args:
        tipo (str): 'seguidors' o 'threads'
        client (str): handle de l'usuari, per exemple: 'customer.bsky.social'
    """
    if tipo not in {"seguidors", "threads"}:
        raise ValueError("El tipus ha de ser 'seguidors' o 'threads'.")

    carpeta = f"segona_part/{tipo}/grafs_{tipo}"

    patrons = [
        f"graf_{tipo}_{client}*.gt",
        f"graf_{tipo}_{client}*.png"
    ]

    if tipo == "seguidors":
        patrons += [
            "graf_comunitats_*.gt",
            "graf_comunitats_*.png"
        ]

    for patron in patrons:
        ruta_completa = os.path.join(carpeta, patron)
        arxius = glob.glob(ruta_completa)
        for arxiu in arxius:
            os.remove(arxiu)


# Eliminem grafs existents
eliminar_grafs("seguidors", CLIENT)
eliminar_grafs("threads", CLIENT)



# ------- 3. CREACIÓ I EXTRACCIÓ DEL GRAF -------
crear_graf_seguidors.generar_graf_seguidors(CLIENT)
crear_graf_threads.generar_graf_threads(CLIENT)

# Carreguem els grafs
patro = f"graf_seguidors_{CLIENT}.gt"
carpeta = (
    Path(__file__).resolve().parent /
    "segona_part" / "seguidors" / "grafs_seguidors"
)
fitxers = list(carpeta.glob(patro))
graf_seguidors = gt.load_graph(str(fitxers[0]))

patro = f"graf_threads_{CLIENT}.gt"
carpeta = (
    Path(__file__).resolve().parent /
    "segona_part" / "threads" / "grafs_threads"
)
fitxers = list(carpeta.glob(patro))
graf_threads = gt.load_graph(str(fitxers[0]))

handle = graf_threads.vertex_properties["handles"]


# ------- 4. CREACIÓ DE L'INFORME DE TEXT -------
with open(TXT_PATH, "w", encoding="utf-8") as f:
    f.write(f"Bluesky Report per a {CLIENT}\n")
    f.write(f"Data: {DATE}\n\n")
    f.write("Objectius i descripció de l'informe:\n")

    f.write(
        f"""Aquest informe solicitat pel client {CLIENT}, té per finalitat 
recollir i analitzar les estàdistiques i comportaments del mateix client a 
l'app social bluesky, amb l'objectiu de generar una anàlisi exhaustiva i 
professional orientat a examinar el seu exercici i influència en plataformes 
digitals. L'estudi se centra en tres àrees fonamentals: el comportament i la 
composició de la base de seguidors, l'eficàcia i l'abast de les publicacions 
així com la participació en talls de conversa ("threads") dins de l'entorn 
del client. Aquesta anàlisi té com a propòsit principal identificar patrons, 
avaluar l'impacte i l'importància de les publicacions del client per extreure 
conclusions estratègiques per a què el client pugui evolucionar com a usuari 
a l'app social, guanyant seguidors i popularitat.\n\n"""
    )

    f.write("L'informa constarà de dos parts:\n")
    f.write("- Anàlisi del graf de seguidors\n- Anàlisi del graf de threads\n")
    f.write("\n\nANÀLISI GRAF DE SEGUIDORS\n")

    f.write(
        "\nPer visualitzar el graf de seguidors, dirigiu-vos al final del "
        "document i trobareu el graf com a la primera imatge.\n"
    )

    f.write(
        f"""\nEl graf de seguidors s'ha generat a partir de nodes que representen 
cada usuari de la xarxa de seguidors del client, i d'arestes dirigides que 
indiquen la relació de "seguir", és a dir, una fletxa d'A a B indica que A és 
seguidor de B. En concret, el graf en qüestió està compost per un total de 
{graf_seguidors.num_vertices()} seguidors, amb un total de 
{graf_seguidors.num_edges()} relacions de seguiment entre ells.\n"""
    )

    # Comunitats
    graf_per_comunitats = graf_seguidors.copy()
    detectar_comunitats_model_blocs(graf_per_comunitats)

    carpeta = (
        Path(__file__).resolve().parent /
        "segona_part" / "seguidors" / "grafs_seguidors"
    )

    visualitzar_graf(
        graf_per_comunitats,
        "comunitat_bloc",
        f"{str(carpeta)}/graf_comunitats_{CLIENT}.png"
    )

    llista_de_comunitats_amb_n_membres = retornar_estadistiques_comunitats(
        graf_per_comunitats, "comunitat_bloc"
    )

    f.write(
        f"\n1.1 Comunitats: Amb el nostre algoritme de detecció de comunitats "
        f"s'han trobat {len(llista_de_comunitats_amb_n_membres)} comunitats diferents "
        f"i aquest es el graf representant-les:"
    )

    if len(llista_de_comunitats_amb_n_membres) > 15:
        f.write(
            "\nEn la xarxa de seguidors obtinguda, hi ha una quantitat moderada "
            "de comunitats. Per a millorar estadístiques; identifiqueu les més actives "
            "i focalitzeu-hi promocions específiques i redirigiu el tipus de contingut cap on convingui.\n"
        )
    else:
        f.write(
            "\nEn la xarxa de seguidors obtinguda, hi ha una quantitat petita de comunitats. "
            "Cal fer esforços per participar en més comunitats rellevants per ampliar l'abast.\n"
        )

    # Densitat
    densitat_graf = (
        graf_seguidors.num_edges() /
        (graf_seguidors.num_vertices() * (graf_seguidors.num_vertices() - 1))
    ) * 100

    if densitat_graf >= 40:
        f.write(
            f"\n1.2 Densitat:  La densitat del nostre graf és del {densitat_graf:.3f}% , "
            "el que implica que la majoria dels usuaris estan connectats entre si. "
            "Això produeix una alta connectivitat, on la informació es propaga ràpidament, "
            "però també pot generar redundància a les connexions.\n\n"
        )
    else:
        f.write(
            f"\n1.2 Densitat: La densitat del nostre graf és del {densitat_graf:.3f}%, "
            "el que implica que només hi ha una petita fracció de les connexions possibles. "
            "És a dir, la majoria dels usuaris segueixen molt pocs altres. Això es tradueix "
            "en una xarxa amb baixa connectivitat global, on la informació es difon més "
            "lentament, llevat que hi hagi certs usuaris molt seguits que actuïn com a hubs "
            "o influenciadors.\n\n"
        )

    # Influents i receptors
    tupla_info_infl_rece = generar_influents_receptors(graf_seguidors)

    f.write(
        "1.3 Influents i receptors: Mitjançant els graus de sortida i d'entrada dels nodes, "
        "s'han detectat tant a persones influents (amb gran quantitat de seguidors) com a "
        "usuaris receptors d'informació (amb gran quantitat de seguits). En aquestes dues "
        f"categories destaquen, respectivament els següents usuaris:\n"
        f"-Influents: {tupla_info_infl_rece[0]}\n"
        f"-Receptors: {tupla_info_infl_rece[1]}\n"
    )

    if tupla_info_infl_rece[0][0][1] > 5000:
        f.write(
            f"\nCom s'han trobat persones prou influents a la xarxa del client, com en "
            f"{tupla_info_infl_rece[0][0][0]}, que té {tupla_info_infl_rece[0][0][1]} seguidors, "
            "caldria treballar o fer colaboracions per amplificar el missatge i fer-se veure.\n\n"
        )
    else:
        f.write(
            "No teniu cap seguidors que superi els 5000 seguidors. Identifiqueu i apropeu-vos a "
            "possibles influencers per començar relacions estratègiques.\n\n"
        )

    # Competidors
    llista_ordenada_per_competicio = mostrar_resultats(
        centralitat_proximitat(graf_seguidors),
        graf_seguidors.vertex_properties["handle"]
    )

    n_decompetidors = 0
    competidors = False

    if llista_ordenada_per_competicio[0][1] >= 0.5:
        competidors = True
        percentatge_competicio = llista_ordenada_per_competicio[0][1]

        while percentatge_competicio >= 0.5:
            n_decompetidors += 1
            percentatge_competicio = llista_ordenada_per_competicio[n_decompetidors][1]

    competidors_sense_mesura = [
        competidor[0] for competidor in llista_ordenada_per_competicio[:n_decompetidors]
    ]

    if competidors:
        f.write(
            f"1.4 Competidors: Hem trobat {n_decompetidors} possible/s competidor/s amb el nostre "
            f"algoritme, que són: {competidors_sense_mesura}. Analitzeu les estratègies de "
            f"competidors com {competidors_sense_mesura[0]}, que és el competidor més directe, "
            "i diferencieu-vos amb contingut únic per guanyar popularitat\n"
        )
    else:
        f.write(
            f"1.4 Competidors: No s'han identificat competidors clau entre els seguidors, "
            f"el que estaria més aprop és {llista_ordenada_per_competicio[0][0]}, amb un "
            f"percentatge de competició de "
            f"{llista_ordenada_per_competicio[0][1]*100:.3f}%, feu un estudi de mercat per detectar nous actors.\n"
        )

    # Reputació
    llista_ordenada_per_reputacio = calcular_top_reputacio(graf_seguidors)

    f.write(
        "\n1.5 Reputació: Amb els nostres algoritmes també hem ordenat els seguidors "
        "del usuari segons la seva reputació per a tal d'obtenir informació sobre els "
        "usuaris més valuosos.\n"
    )
    f.write(f"Aquests son els 5 primers: {llista_ordenada_per_reputacio[:5]}\n")


    f.write(f"\n\nANÀLISI GRAF DE THREADS\n\n")

    pes = graf_threads.edge_properties["weight"]
    aresta_de_maxim_pes = next(graf_threads.edges())
    suma_pesos = pes[aresta_de_maxim_pes]
    maxim_pes = pes[aresta_de_maxim_pes]

    for e in graf_threads.edges():
        suma_pesos += pes[e]
        if pes[e] > maxim_pes:
            maxim_pes = pes[e]
            aresta_de_maxim_pes = e

    f.write(
        f"""Aquest graf modela l'estructura del flux de interaccions que comencen amb el client, 
    on cada node representa una persona o que ha participat en algun "thread" on hagi participat 
    també el client,  i les arestes van d'un usuari a un altre que hagi interactuat amb una 
    publicació del primer.\n\nEn el cas de {CLIENT} hi han {suma_pesos} interaccions i 
    {graf_threads.num_vertices()} persones que han intractuat. El màxim nombre d'innteraccions entre 
    dos usuaris ha sigut {maxim_pes}, de {handle[aresta_de_maxim_pes.target()]} cap a 
    {handle[aresta_de_maxim_pes.source()]}."""
    )

    if suma_pesos < 50:
        f.write(
            " Hi ha menys de 50 interaccions en threads. Cal millorar la participació mitjançant "
            "tècniques d'engagment.\n\n"
        )
    else:
        f.write(
            "S'observa una bona dinàmica i participació en els threads del del client.\n\n"
        )

    f.write(
        f"""A l'hora de profunditar en l'informació que ens dona el graf obtingut, hem decidit 
    centrar-nos en dos aspectes diferents, els vèrtex de sortida i els punts de pas. En un graf de 
    fils de conversa ("threads"), un punt de pas (o node d'articulació) és un node concret la 
    presència del qual manté connectats dos o més subfils i que pertant són claus pel desenvolupament 
    de la conversa. Per altre banda, els nodes de sortida són aquells vèrtexs que tenen moltes arestes 
    que connecten amb usuaris que no segueixen al client. Són, per tant, punts des d'on "s'escampa" la 
    informació cap a usuaris desconeguts.\n\nEls resultats obtinguts són els següents:\n"""
    )

    # Punts de pas

    f.write("\n2.1 Punts de pas:\n")

    llista_punts_de_pas = generar_punts_de_pas(CLIENT, graf_threads)

    if llista_punts_de_pas:
        llargada_de_la_llista_de_punts_de_pas = min(len(llista_punts_de_pas), 10)

        f.write(
            "Els 10 usuaris que apareixen més com a punts de pas (intermediaris) són:\n"
        )

        for idx, (handle_punt, compte_punt) in enumerate(
            llista_punts_de_pas[:llargada_de_la_llista_de_punts_de_pas], start=1
        ):
            # Personalització segons nombre de vegades com a punt de pas
            if compte_punt > 20:
                nota = " (Excel·lent canal de difusió!)"
            elif compte_punt > 10:
                nota = " (Bona influència en el flux de conversa)"
            else:
                nota = ""
            f.write(f"{idx}. {handle_punt}: {compte_punt} vegades{nota}\n")
            f.write("\n")

        f.write(
            "S'ha de cuidar la relació amb aquests usuaris, ja que canalitzen molta de la exposició "
            "del client. També s'hauria de mirar de no crear una relació de dependencia amb aquests, "
            "i intentar crear una línia directa de interaccions.\n"
        )
    else:
        f.write(
            "Les publicacions del client no són suficientment prolífiques com per a que hi hagin punts "
            "de pas, aixó demostra que el client encara té molt potencial d'expansió i hauria de buscar "
            "formes de incrementar la seva exposició a Bluesky.\n"
        )

    # Vèrtexs de sortida

    f.write(
        "\n2.2 Vèrtexs de sortida: Els vèrtexs de sortida són una mesura molt important per veure qui "
        "són aquells usuaris que porten el contingut del client a  nous públics, que no estan presents "
        "a la base de seguidors acutal.\n"
    )

    comptador_sortides_threads = vertexs_de_sortida(graf_threads, graf_seguidors)

    if not comptador_sortides_threads:
        f.write(
            "\nNo s'ha detectat cap vèrtex que sigui seguidor directe del client amb sortides cap a "
            "usuaris fora de la base de seguidors.\n\n"
        )
    else:
        f.write(
            "\nEls 10 usuaris seguidors que transmeten més converses fora de la base de seguidors "
            "(vèrtexs de sortida):\n"
        )
        for idx, (handle_sortida, compte_sortida) in enumerate(
            comptador_sortides_threads, start=1
        ):
            # Personalització segons sortides
            if compte_sortida > 15:
                comentari = " (Divulgador principal cap a públic extern!)"
            elif compte_sortida > 5:
                comentari = " (Bona connexió amb noves audiències)"
            else:
                comentari = ""
            f.write(f"{idx}. {handle_sortida}: {compte_sortida} sortides{comentari}\n")
        f.write(
            "\nCal tenir en compte els usuaris que serveixen com a node de sortida a nous públics i "
            "investigar les potencials audiències per a enfocar millor el contingut. També cuidar la "
            "relació amb aquests usuaris, ja que funcionen com una porta a usuaris desconeguts que pot "
            "ser molt valiosa.\n"
        )




# ------- 5. CREACIÓ DEL PDF AMB fpdf2 -------
pdf = FPDF(unit="cm", format="A4")
pdf.set_auto_page_break(auto=True, margin=1.5)
pdf.add_page()
pdf.set_font("Arial", size=12)
line_height = pdf.font_size * 1.5

with open(TXT_PATH, "r", encoding="utf-8") as f:
    for line in f:
        pdf.multi_cell(18, line_height, line.rstrip(), align='L')

pdf.image(
    f"segona_part/seguidors/grafs_seguidors/graf_seguidors_{CLIENT}.png",
    x=1,
    y=None,
    w=18,
)
pdf.image(
    f"segona_part/seguidors/grafs_seguidors/graf_comunitats_{CLIENT}.png",
    x=1,
    y=None,
    w=18,
)
pdf.image(
    f"segona_part/threads/grafs_threads/graf_threads_{CLIENT}.png",
    x=1,
    y=None,
    w=18,
)

pdf.output(PDF_PATH)

os.remove(TXT_PATH)

print(f"Report generat: {PDF_PATH}")




