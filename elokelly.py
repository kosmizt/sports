import requests
from bs4 import BeautifulSoup

def baixar_elos():
    url = "https://tennisabstract.com/reports/atp_elo_ratings.html"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tr")
    elo_dict = {}

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 9:
            nome = cols[1].get_text().strip()
            try:
                elo = float(cols[3].get_text().strip())
                cElo = float(cols[8].get_text().strip())  # clay
                hElo = float(cols[6].get_text().strip())  # hard
                gElo = float(cols[10].get_text().strip())  # grass
                elo_dict[nome] = {"elo": elo, "cElo": cElo, "hElo": hElo, "gElo": gElo}
            except ValueError:
                continue
    return elo_dict


def resolver_nome(nome_parcial, elo_dict):
    matches = [n for n in elo_dict if nome_parcial.lower() in n.lower()]
    if len(matches) == 0:
        print(f"Erro. Algum jogador não foi encontrado.")
        return None
    elif len(matches) == 1:
        return matches[0]
    else:
        print(f"Foram encontradas {len(matches)} correspondências para '{nome_parcial}':")
        for i, n in enumerate(matches):
            print(f"{i+1}. {n}")
        while True:
            try:
                escolha = int(input("Escolha o número correspondente: "))
                if 1 <= escolha <= len(matches):
                    return matches[escolha-1]
            except ValueError:
                pass
            print("Entrada inválida. Tente novamente.")


def obter_elo_superficie(elos, superficie):
    superficie = superficie.lower()
    if superficie == "saibro":
        return (elos["elo"] + elos["cElo"]) / 2
    elif superficie == "quadra dura":
        return (elos["elo"] + elos["hElo"]) / 2
    elif superficie == "grama":
        return (elos["elo"] + elos["gElo"]) / 2
    else:
        return elos["elo"]


def elokelly(e1, e2, o1, o2, m, b, j):
    """para dois jogadores, sem a possibilidade de empate
       e1 = elo do jogador 1
       e2 = elo do jogador 2
       o1 = odds para jogador 1
       o2 = odds para jogador 2
       m = multiplicador, a fração confortável de aposta. decimal
       b = banca
       j = jogador a avaliar"""

    if o1 < 1 or o2 < 1:
        raise ValueError("valores de odd devem ser superiores a 1")

    p1 = 1 - (1 / (1 + (10**((e1-e2) / 400))))
    p2 = 1 - (1 / (1 + (10**((e2-e1) / 400))))

    k1 = b*m*((p1)-((1-p1)/(o1-1)))
    k2 = b*m*((p2)-((1-p2)/(o2-1)))

    if j == 1:
        print(f"probabilidade de vitória do jogador: {p1}", end='\n')
        print(f"o quanto se deveria apostar: {k1}", end='\n')

        if k1 <= 0:
            print(f"a aposta não é aconselhada, por retornos negativos")

    elif j == 2:
        print(f"probabilidade de vitória do jogador: {p2}", end='\n')
        print(f"o quanto se deveria apostar: {k2}", end='\n')

        if k2 <= 0:
            print(f"a aposta não é aconselhada, por retornos negativos")


def main():
    print("Elo ratings (retirados de tennisabstract.com)")
    elo_dict = baixar_elos()
    print(f"{len(elo_dict)} jogadores carregados.\n")

    nome1 = resolver_nome(input("Jogador 1: "), elo_dict)
    nome2 = resolver_nome(input("Jogador 2: "), elo_dict)
    if not nome1 or not nome2:
        print("Não foi possível identificar os jogadores.")
        return

    superficie = input("Superfície (geral / saibro / quadra dura / grama): ").strip().lower()

    e1 = obter_elo_superficie(elo_dict[nome1], superficie)
    e2 = obter_elo_superficie(elo_dict[nome2], superficie)

    o1 = float(input(f"Odd para {nome1}: "))
    o2 = float(input(f"Odd para {nome2}: "))
    m = float(input("Multiplicador: "))
    b = float(input("Banca: "))
    j = int(input("Avaliar jogador 1 ou 2? "))

    elokelly(e1, e2, o1, o2, m, b, j)

if __name__ == "__main__":
    main()

