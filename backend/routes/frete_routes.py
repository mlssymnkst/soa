import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("MELHOR_ENVIO_TOKEN")
USER_AGENT = os.getenv("MELHOR_ENVIO_USER_AGENT")

print("TOKEN", TOKEN)
print("USER_AGENT", USER_AGENT)

URL = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate"

def calcular_frete_fallback(valor_total, peso_gramas, endereco):
    if valor_total >= 350:
        return {
            "valor": 0.0,
            "prazo_dias": 7,
            "transportadora": "Frete grátis",
            "origem": "simulado"
        }

    peso_kg = peso_gramas / 1000

    return {
        "valor": round(15.0 + (peso_kg * 3.5), 2),
        "prazo_dias": 5,
        "transportadora": "A definir",
        "origem": "simulado"
    }

def calcular_frete_melhor_envio(
    cep_origem,
    cep_destino,
    largura,
    altura,
    comprimento,
    peso,
    valor_seguro
):

    # Se não tiver token configurado, usa fallback
    if not TOKEN or TOKEN == "SEU_TOKEN":
        print("Token Melhor Envio não configurado. Usando frete simulado.")

        return calcular_frete_fallback(
            valor_total=valor_seguro,
            peso_gramas=peso * 1000,
            endereco=cep_destino
        )

    payload = {
        "from": {
            "postal_code": cep_origem
        },
        "to": {
            "postal_code": cep_destino
        },
        "volumes": [
            {
                "width": largura,
                "height": altura,
                "length": comprimento,
                "weight": peso,
                "insurance": valor_seguro
            }
        ],
        "options": {
            "receipt": False,
            "own_hand": False
        },
        "services": "1,2,18"
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": USER_AGENT
    }

    try:

        response = requests.post(
            URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            print("Erro Melhor Envio:", response.text)

            return calcular_frete_fallback(
                valor_total=valor_seguro,
                peso_gramas=peso * 1000,
                endereco=cep_destino
            )

        dados = response.json()

        fretes_validos = [
            frete for frete in dados
            if "error" not in frete
        ]

        if not fretes_validos:

            return calcular_frete_fallback(
                valor_total=valor_seguro,
                peso_gramas=peso * 1000,
                endereco=cep_destino
            )

        melhor = min(
            fretes_validos,
            key=lambda f: float(
                f.get("custom_price", f.get("price", 999999))
            )
        )

        return {
            "transportadora": melhor.get("company", {}).get("name"),
            "servico": melhor.get("name"),
            "valor": float(
                melhor.get("custom_price", melhor.get("price"))
            ),
            "prazo_dias": melhor.get(
                "custom_delivery_time",
                melhor.get("delivery_time")
            ),
            "origem": "melhor_envio"
        }

    except Exception as e:

        print("Erro ao consultar Melhor Envio:", e)

        return calcular_frete_fallback(
            valor_total=valor_seguro,
            peso_gramas=peso * 1000,
            endereco=cep_destino
        )


# def calcular_frete_melhor_envio(
#     cep_origem,
#     cep_destino,
#     largura,
#     altura,
#     comprimento,
#     peso,
#     valor_seguro
# ):

#     payload = {
#         "from": {
#             "postal_code": cep_origem
#         },
#         "to": {
#             "postal_code": cep_destino
#         },
#         "volumes": [
#             {
#                 "width": largura,
#                 "height": altura,
#                 "length": comprimento,
#                 "weight": peso,
#                 "insurance": valor_seguro
#             }
#         ],
#         "options": {
#             "receipt": False,
#             "own_hand": False
#         },
#         "services": "1,2,18"
#     }

#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {TOKEN}",
#         "User-Agent": USER_AGENT
#     }

#     response = requests.post(URL, json=payload, headers=headers)

#     if response.status_code != 200:
#         print(response.text)
#         return None

#     dados = response.json()

#     fretes_validos = [
#         frete for frete in dados
#         if "error" not in frete
#     ]

#     if not fretes_validos:
#         return None

#     melhor = min(
#         fretes_validos,
#         key=lambda f: float(f.get("custom_price", f.get("price", 999999)))
#     )

#     return {
#         "transportadora": melhor.get("company", {}).get("name"),
#         "servico": melhor.get("name"),
#         "valor": float(melhor.get("custom_price", melhor.get("price"))),
#         "prazo_dias": melhor.get("custom_delivery_time", melhor.get("delivery_time"))
#     }


    