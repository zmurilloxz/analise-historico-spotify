# Projeto de análise dos dados Spotify
# Murillo Alcantara
# Período dos dados - 05/11/2025 - 05/11/2026

import pandas as pd
import matplotlib.pyplot as plt

# "from ... import" pega SÓ UMA PEÇA da biblioteca (o Path), não ela inteira (da biblioteca inteira da pathlib, pega apenas o path)
from pathlib import Path

#===============================================================

# __file__ = endereço completo DESTE arquivo
# .parent  = "pai" = a pasta onde o arquivo está (spot_project)
# Assim o caminho funciona em qualquer PC, sem depender de onde o PyCharm roda
PASTA_PROJETO = Path(__file__).parent

# A "/" aqui NÃO é divisão: JUNTA pedaços do caminho (pasta → pasta)
# "dados" e "Spotify Account Data" são PASTAS. A variável só guarda o endereço
PASTA_DADOS = PASTA_PROJETO / "dados" / "Spotify Account Data"

# acesso à pasta de gráficos
PASTA_GRAFICOS = PASTA_PROJETO / "graficos"

# essa variável guarda o tempo minimo para contagem de reprodução = 30 Segundos = 30000 milissegundos
TEMPO_MINIMO_MS = 30000

# essa variavel guarda horas em milissegundos = 1 hora = 3600000
TEMPO_HORAS = 3600000

# essa variavel guarda os ruídos
ARTISTAS_RUIDO = ["Sleep Miracle", "Lavender Balm", "Ardeon", "Harper Rems", "Hybrid Treasure", "The Floating Mind", "chamberecho", "Fortuna", "Hum Humming", "Limone M", "Klangspiel", "Optura", "Bits & Noise", "Brainbox", "HQ-10", "Alex Slumber", "Dancing Waves", "Mentatranque"]

# essa variavel guarda um valor minimo de reproduções
MINIMO_REPRODUCOES = 100
#===============================================================

# df	Tudo: ouvidas e puladas (20938)	Tudo que precisa das puladas

# ouvidas	Só o que passou de 30 s (15735)	Horas, dias, tops de artistas

# músicas	ouvidas sem os ruídos (15180)	Análises de gosto musical

#===============================================================

# 1. carregar os dados
# lendo cada arquivo
df0 = pd.read_json(PASTA_DADOS / "StreamingHistory_music_0.json")
df1 = pd.read_json(PASTA_DADOS / "StreamingHistory_music_1.json")
df2 = pd.read_json(PASTA_DADOS / "StreamingHistory_music_2.json")

#================================================================

# mostrando linhas que foram carregadas
print(df0.shape, df1.shape, df2.shape)

# As tabelas vão numa LISTA [ ] → o concat recebe um "pacote" com tudo pra juntar
# juntando as 3 tabelas numa só (ignore_index renumera as linhas de 0 a 20937
df = pd.concat([df0, df1, df2], ignore_index=True)

# Mostra o total de linhas carregadas . Linhas carregadas 20938
print( "Linhas carregadas:",df.shape[0])

# ===============================================================

# 2 limpeza

# filtra só as músicas ouvidas por 30 segundos ou mais (tira as músicas que foram puladas antes de 30 sec)
ouvidas = df[df["msPlayed"] >= TEMPO_MINIMO_MS]

# resumo da limpeza: antes, depois e quantas foram removidas
print("Quantas linhas antes:", df.shape[0])
print("Quantas linhas depois:", ouvidas.shape[0])
print("Quantas foram removidas:", df.shape[0] - ouvidas.shape[0])

# transforma o endTime (texto) em data, no horário de Brasília
# o Spotify grava em UTC (Londres), 3 horas à frente do Brasil
ouvidas["data"] = pd.to_datetime(ouvidas["endTime"], utc=True).dt.tz_convert("America/Sao_Paulo")

# cria a coluna com só a hora de cada música
ouvidas["hora"] = ouvidas["data"].dt.hour

# cria a coluna com o dia da semana (em inglês)
ouvidas["dia_da_semana"] = ouvidas["data"].dt.day_name()
#print(ouvidas.head())

#===============================================================

# 3 analises

# Calculo para verificar o total de horas ouvidas. o 60000 seria 1 minuto
total_min = (ouvidas["msPlayed"].sum() //60000)
horas = total_min // 60
minutos = total_min % 60
print("Total:", horas, "horas", minutos, "minutos")

# Verifica a quantidade de artistas diferentes que foram escutados. (o nunique verifica os artistas iguais e não soma eles)
qtd_artistas = ouvidas["artistName"].nunique()
print("Total de artistas:", qtd_artistas)

# Verifica a quantidade de músicas diferentes que foram escutadas. (nunique verifica as músicas que não repetiram)
# Uma música é o PAR (artista + nome): "Intro" de dois artistas diferentes são músicas diferentes
qtd_musicas = ouvidas[["artistName", "trackName"]].drop_duplicates().shape[0]
print("Total de musicas:", qtd_musicas)

#=======================================================

# verificar top 10 artistas por horas ouvidas
# versão antes de separar os ruídos
horas_artista = (ouvidas.groupby("artistName") ["msPlayed"].sum() / TEMPO_HORAS).round(1)
top10_artistas = horas_artista.sort_values(ascending=False).head(10)
print("Top 10 artistas mais ouvidos:")
print(top10_artistas)

# verifica o top 10 músicas por quantidade de vezes ouvidas
# agrupa por artista + música (e não só pelo nome), para não somar músicas de mesmo nome de artistas diferentes
top10_musicas = ouvidas.groupby(["artistName", "trackName"]).size().sort_values(ascending=False).head(10)
print("Top 10 musicas mais ouvidas:")
print(top10_musicas)

#======================================================

# 3.5 separar ruídos

# investigando os ruídos, descobrindo qual artista
ruido1 = ouvidas[ouvidas["trackName"] == "Brown Sleep Noise"]
ruido_artista = ruido1["artistName"].value_counts()
#print("artista ruido 1:")
#print(ruido_artista)

ruido2 = ouvidas[ouvidas["trackName"] == "Settled Space"]
ruido2_artista = ruido2["artistName"].value_counts()
#print("artista ruido 2:")
#print(ruido2_artista)

ruido3 = ouvidas[ouvidas["trackName"] == "Ruido De Aviones Freq 238 Hz Q 0.5 - Seamless"]
ruido3_artista = ruido3["artistName"].value_counts()
#print("artista ruido 3:")
#print(ruido3_artista)

# ↑ foram descobertos os 11 artistas principais Sleep Miracle, Lavender Balm, Ardeon, Harper Rems, Hybrid Treasure, The Floating Mind, chamberecho, Fortuna, Hum Humming, Limone M, Mentatranque.
# depois a lista foi ampliada para 18 artistas (veja a constante ARTISTAS_RUIDO no topo)

# investigando os ruídos para descobrir se tem mais faixas além das que estão no top 10

faixas_sleep = ouvidas[ouvidas["artistName"] == "Sleep Miracle"]
faixas_sleep_miracle = faixas_sleep["trackName"].value_counts()
#print("Faixas do Sleep Miracle:")
#print(faixas_sleep_miracle)

faixas_lavender = ouvidas[ouvidas["artistName"] == "Lavender Balm"]
faixas_lavender_balm = faixas_lavender["trackName"].value_counts()
#print("Faixas do Lavender Balm:")
#print(faixas_lavender_balm)

faixas_ard = ouvidas[ouvidas["artistName"] == "Ardeon"]
faixas_ardeon = faixas_ard["trackName"].value_counts()
#print("Faixas do Ardeon:")
#print(faixas_ardeon)

faixas_harper = ouvidas[ouvidas["artistName"] == "Harper Rems"]
faixas_harper_rems = faixas_harper["trackName"].value_counts()
#print("Faixas do Harper Rems:")
#print(faixas_harper_rems)

faixas_hybrid = ouvidas[ouvidas["artistName"] == "Hybrid Treasure"]
faixas_hybrid_treasure = faixas_hybrid["trackName"].value_counts()
#print("Faixas do Hybrid Treasure:")
#print(faixas_hybrid_treasure)

# 3.5 etapa 2: separar ruídos de dormir

ruidos = ouvidas[ouvidas["artistName"].isin(ARTISTAS_RUIDO)]
# print("Ruídos:")
# print("Ruídos separados:", ruidos.shape[0])

#==================================================================

# tabela músicas

musicas = ouvidas[~ouvidas["artistName"].isin(ARTISTAS_RUIDO)]
# print("Músicas:")
# print("Músicas separadas:", musicas.shape[0])

# checagem de ruídos
# filtrar músicas tem "NOISE" no nome
suspeitas_noise = musicas[musicas["trackName"].str.contains("Noise", case=False)]
# print("Suspeitas noise:")
# print(suspeitas_noise)

artistas_suspeitos = suspeitas_noise["artistName"].value_counts()
# print("Artistas suspeitos:")
# print(artistas_suspeitos.head(10))

# descobrir se esses artistas são realmente dos ruídos
# faixa_floating = musicas[musicas["artistName"] == "The Floating Mind"]
# faixa_floating_mind = faixa_floating["trackName"].value_counts()
# print("Faixas do Floating Mind:")
# print(faixa_floating_mind)

# contar faixas de suspeita noise
qtd_suspeitas_noise = suspeitas_noise["trackName"].value_counts()
# print("quantidade suspeitas noise:")
# print(qtd_suspeitas_noise)

# ===================== Filtrar músicas pelo artista ======================

# faixas chamberecho
# chamberecho: ruido (loopable noise)
# faixa_chamber = musicas[musicas["artistName"] == "chamberecho"]
# faixa_chamberecho = faixa_chamber["trackName"].value_counts()
# print("Faixas do Chamberecho:")
# print(faixa_chamberecho)

# faixas Fortuna
# Fortuna: ruido (maioria; "Satellite" 1x vai junto)
# faixa_fort = musicas[musicas["artistName"] == "Fortuna"]
# faixa_fortuna = faixa_fort["trackName"].value_counts()
# print("Faixas do Fortuna:")
# print(faixa_fortuna)

# faixas hum humming
# Hum Humming: ruido (brown noise)
# faixa_hum = musicas[musicas["artistName"] == "Hum Humming"]
# faixa_humming = faixa_hum["trackName"].value_counts()
# print("Faixas do Hum Humming:")
# print(faixa_humming)

# faixas Limone M
# Limone M: ruido
# faixa_lim = musicas[musicas["artistName"] == "Limone M"]
# faixa_limone = faixa_lim["trackName"].value_counts()
# print("Faixas do Limone M:")
# print(faixa_limone)

# faixas Klangspiel
# Klangspiel: ruido
# faixa_klang = musicas[musicas["artistName"] == "Klangspiel"]
# faixa_klangspiel = faixa_klang["trackName"].value_counts()
# print("Faixas do Klangspiel:")
# print(faixa_klangspiel)

# faixas Optura
# Optura: ruido
# faixa_opt = musicas[musicas["artistName"] == "Optura"]
# faixa_optura = faixa_opt["trackName"].value_counts()
# print("Faixas do Optura:")
# print(faixa_optura)

# faixas Bits & Noise
# Bits & Noise: ruido
# faixa_bit= musicas[musicas["artistName"] == "Bits & Noise"]
# faixa_bits = faixa_bit["trackName"].value_counts()
# print("Faixas do Bits & Noise:")
# print(faixa_bits)

# faixas Brainbox
# Brainbox: ruido
# faixa_brain = musicas[musicas["artistName"] == "Brainbox"]
# faixa_brainbox = faixa_brain["trackName"].value_counts()
# print("Faixas do Brainbox:")
# print(faixa_brainbox)

# faixas HQ-10
# HQ-10: ruido
# faixa_h = musicas[musicas["artistName"] == "HQ-10"]
# faixa_hq = faixa_h["trackName"].value_counts()
# print("Faixas do HQ-10:")
# print(faixa_hq)

# faixas Alex Slumber
# Alex Slumber: ruido
# faixa_alex = musicas[musicas["artistName"] == "Alex Slumber"]
# faixa_alex_slumber = faixa_alex["trackName"].value_counts()
# print("Faixas do Alex Slumber:")
# print(faixa_alex_slumber)

# faixas Dancing Waves
# Dancing Waves: ruido
# faixa_dance = musicas[musicas["artistName"] == "Dancing Waves"]
# faixa_dancing = faixa_dance["trackName"].value_counts()
# print("Faixas do Dancing Waves:")
# print(faixa_dancing)


# descobrir artista da musica brown bliss 250 hz q 1 - seamless - - - - - - foi descoberto que era Mentatranque
# faixa_seam = musicas[musicas["trackName"].str.contains("Seam", case=False)]
# print("Qual artista é:")
# print(faixa_seam)


# faixas Mentatranque
# Mentatranque: ruido
# faixa_menta = musicas[musicas["artistName"] == "Mentatranque"]
# faixa_mentatranque = faixa_menta["trackName"].value_counts()
# print("Faixas mentatranque:")
# print(faixa_mentatranque)


# total de horas na tabela músicas constante = TEMPO_HORAS
horas_musicas = (musicas["msPlayed"].sum() / TEMPO_HORAS)
total_horas_musicas = horas_musicas // 1
total_minutos_musicas = horas_musicas  % 1 * 60
print("A tabela musica tem", round(total_horas_musicas), "horas e", round(total_minutos_musicas), "minutos")

# numero de artistas e músicas diferentes na tabela músicas
qtd_artistas_diferentes = musicas["artistName"].nunique()
print("Quantidade de artistas diferentes:", qtd_artistas_diferentes)

qtd_musicas_diferentes = musicas[["artistName", "trackName"]].drop_duplicates().shape[0]
print("Quantidade de musicas diferentes:", qtd_musicas_diferentes)

# top 10 artistas em horas

todos_artistas_horas = (musicas.groupby("artistName")["msPlayed"].sum() / TEMPO_HORAS).round(1).sort_values(ascending=False)
print("Top 10 artistas em horas:")
print(todos_artistas_horas.head(10))

# top 10 músicas
# groupby com 2 colunas: a chave é o par (artista, música). O size() conta as linhas de cada par
todas_musicas = musicas.groupby(["artistName", "trackName"]).size().sort_values(ascending=False)
print("Top 10 músicas mais ouvidas:")
print(todas_musicas.head(10))

# horas dos ruídos
horas_ruidos = (ruidos["msPlayed"].sum() / TEMPO_HORAS)
total_horas_ruidos = horas_ruidos // 1
total_minutos_ruidos = horas_ruidos % 1 * 60
print("A tabela ruídos tem", round(total_horas_ruidos), "horas", round(total_minutos_ruidos), "minutos")

# Os ruídos são cerca de 3,6% do tempo total. Pouco no tempo total, mas o suficiente para distorcer o top 10 músicas.
# Informações mostrando antes e após separar os ruídos

# Total de horas = 790 horas e 41 minutos (antes 820 horas e 33 minutos)
# Artistas diferentes = 493 (antes 511)
# Músicas diferentes = 1874 (antes 1934)
# Top 10 artistas em horas: sem mudança (ruídos eram muitas reproduções curtas de artistas pouco ouvidos)
# No top 10 músicas saíram 4 ruídos: Brown Sleep Noise (115), Settled Space (105), Ruido De Aviones (93) e Brown Bliss - Mentatranque (89); entraram ai se eu te amasse (85), DM (84) e Camisa Cortada

# foi escolhido a tabela ouvidas para poder incluir todas as reproduções

# conta quantas reproduções caem em cada hora
rep_horas = ouvidas["hora"].value_counts().sort_index()
print("Quantas reproduções caem em cada hora do dia")
print(rep_horas)

# conta quais dias da semana mais reproduz
rep_semana = ouvidas["dia_da_semana"].value_counts()
print("Quais dias da semana tem mais reproduções:")
print(rep_semana)

# contas as horas usando a tabela músicas
rep_musicas_horas = musicas["hora"].value_counts().sort_index()
print("Quantas reproduções caem em cada hora do dia")
print(rep_musicas_horas)

# quantas reproduções de ruído caem em cada hora (com ruído - sem ruído)
dif_ruidos_horas = rep_horas - rep_musicas_horas
# print("Diferença entre as reproduções com ruído e sem ruído")
# print(dif_ruidos_horas)

# descobrir total de reproduções de ruídos
total_ruidos = dif_ruidos_horas.sum()
print("Total de reproduções de ruído")
print(total_ruidos)

# coluna pulou: True = reprodução com menos de 30 s (foi pulada), False = ouvida
df["pulou"] = df["msPlayed"] < TEMPO_MINIMO_MS

# taxa geral de pulo (mean de True/False = fração de True)
taxa_pulo_geral = df["pulou"].mean() * 100
print("Taxa geral de pulo:")
print(round(taxa_pulo_geral, 1))

# 2 reproduções tinham exatamente 30000 ms (NX Zero e Matuê), por isso ouvidas usa >=
# iguais_30s = df[df["msPlayed"] == TEMPO_MINIMO_MS]
# print(iguais_30s)

# taxa de pulo por artista. a constante (MINIMO_REPRODUCOES) vai ser 100 para obter uma precisão melhor, e não vamos usar os ruídos.
qtd_pulo_df = df["pulou"].sum()
print("Total de reproduções puladas:")
print(qtd_pulo_df)

df_sem_ruido = df[~df["artistName"].isin(ARTISTAS_RUIDO)]
print("Tabela sem ruídos:")
print(df_sem_ruido.shape[0])

#------------------------------------------------------
# Unknown Artist é rótulo sem informação (148 reprod., todas < 30 s); tirado do ranking
df_artista = df_sem_ruido[df_sem_ruido["artistName"] != "Unknown Artist"]
#print(df_artista)
#-------------------------------------------------------

pulos_artistas = df_artista.groupby("artistName")["pulou"].agg(["mean", "count"])
#print("Agrupado por artistas:")
#print(pulos_artistas)

soma_count_pa = pulos_artistas["count"].sum()
print("Soma da coluna count")
print(soma_count_pa)

pulos_minimos = pulos_artistas[pulos_artistas["count"] >= MINIMO_REPRODUCOES]
#print("Artistas com o mínimo de reproduções ou mais:")
#print(pulos_minimos)

pulos_minimos["taxa_pulo"] = (pulos_minimos["mean"] * 100).round(1)
ranking_pulos = pulos_minimos["taxa_pulo"].sort_values(ascending=False)
print("Top 10 artistas mais pulados (taxa de pulo em %)")
print(ranking_pulos.head(10))

# unknown = df_sem_ruido[df_sem_ruido["artistName"] == "Unknown Artist"]
# unknown_artist = unknown["trackName"].value_counts()
# print(unknown_artist)

# ===========================================================================

# 4 gráficos PASTA_GRAFICOS

# gráfico top 10 artistas com mais horas
top10_artistas_horas = todos_artistas_horas.sort_values(ascending=False).head(10)
top10_artistas_horas.plot(kind="barh")
plt.gca().invert_yaxis()
plt.title("Top 10 artistas com mais horas reproduzidas")
plt.ylabel("Artistas")
plt.xlabel("Horas")
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / "top10_artistas_horas.png")
plt.show()
plt.close()

# gráfico top 10 músicas
# o índice agora é (artista, música); transforma em texto "Música - Artista" para aparecer bonito no gráfico
top10_musicas_tocadas = todas_musicas.sort_values(ascending=False).head(10)
top10_musicas_tocadas.index = [f"{musica} - {artista}" for artista, musica in top10_musicas_tocadas.index]
top10_musicas_tocadas.plot(kind="barh")
plt.gca().invert_yaxis()
plt.title("Top 10 músicas com mais vezes tocadas")
plt.ylabel("Músicas")
plt.xlabel("Vezes")
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / "top10_musicas_vezes.png")
plt.show()
plt.close()

# gráfico da taxa de pulo (top 10 artistas)
top10_pulos_taxa = ranking_pulos.head(10)
top10_pulos_taxa.plot(kind="barh")
plt.gca().invert_yaxis()
plt.title(f"Top 10 artistas mais pulados ({MINIMO_REPRODUCOES}+ reproduções)")
plt.ylabel("Artistas")
plt.xlabel("% de pulo")
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / "top10_pulos_taxa.png")
plt.show()
plt.close()

# gráfico das horas do dia
rep_horas.plot(kind="bar", rot=0)
plt.title("Reproduções por hora")
plt.ylabel("Reproduções")
plt.xlabel("Horas do dia")
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / "reproducoes_por_horas.png")
plt.show()
plt.close()

# gráfico dias da semana (Seg -> Dom)
lista_semana = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dicionario = {"Monday": "Segunda",
              "Tuesday": "Terça",
              "Wednesday": "Quarta",
              "Thursday": "Quinta",
              "Friday": "Sexta",
              "Saturday": "Sábado",
              "Sunday": "Domingo"}
rep_semana_ordenada = rep_semana.reindex(lista_semana).rename(index=dicionario)
rep_semana_ordenada.plot(kind="bar", rot=0)
plt.title("Reproduções por dia da semana")
plt.ylabel("Reproduções")
plt.xlabel("Dia da semana")
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / "reproducoes_por_dia_da_semana.png")
plt.show()
plt.close()

# prova real
print(rep_semana_ordenada.sum())