import sqlite3
import requests
import os

def criar_tabelas(db_path):
    """Cria as tabelas no banco de dados se não existirem."""
    tabelas = {
        "CREATE_TABLE_ESTADOS": """
            CREATE TABLE IF NOT EXISTS estados (
                id INTEGER PRIMARY KEY NOT NULL, 
                nome VARCHAR(200) NOT NULL
            );
        """,
        "CREATE_TABLE_CIDADES": """
            CREATE TABLE IF NOT EXISTS cidades (
                id INTEGER PRIMARY KEY NOT NULL, 
                codigo_igbe VARCHAR(200) NOT NULL,
                nome VARCHAR(200) NOT NULL
            );
        """,
        "CREATE_TABLE_ENTIDADE": """
            CREATE TABLE IF NOT EXISTS entidades (
                id INTEGER PRIMARY KEY NOT NULL, 
                codigo_igbe VARCHAR(200) NOT NULL,
                nome VARCHAR(200) NOT NULL
            );
        """,
    }

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for tabela in tabelas.values():
        cursor.execute(tabela)
    conn.commit()
    conn.close()

def sincronizar_dados(api_url, tabela, db_path):
    """Sincroniza os dados da API com a tabela do banco de dados."""
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        dados = response.json()

        # Verifica se os dados estão na chave 'data'
        if isinstance(dados, dict) and "data" in dados:
            dados = dados["data"]

        if not isinstance(dados, list):
            raise ValueError(f"Os dados da API {api_url} não estão no formato esperado.")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if tabela == "estados":
            cursor.execute("DELETE FROM estados")
            for estado in dados:
                estado_id = int(estado.get("id"))
                estado_nome = estado.get("name")  # Ajustado para a chave 'name'
                if estado_id and estado_nome:
                    cursor.execute("INSERT INTO estados (id, nome) VALUES (?, ?)", (estado_id, estado_nome))
        
        elif tabela == "cidades":
            cursor.execute("DELETE FROM cidades")
            for cidade in dados:
                cidade_id = int(cidade.get("id"))
                cidade_nome = cidade.get("name")  # Ajustado para a chave 'name'
                if cidade_id and cidade_nome:
                    cursor.execute(
                        "INSERT INTO cidades (id, codigo_igbe, nome) VALUES (?, ?, ?)",
                        (cidade_id, cidade_id, cidade_nome),  # Código IBGE é igual ao ID neste caso
                    )
        
        elif tabela == "entidades":
            cursor.execute("DELETE FROM entidades")
            for entidade in dados:
                entidade_id = int(entidade.get("id"))
                entidade_nome = entidade.get("name")  # Ajustado para a chave 'name'
                if entidade_id and entidade_nome:
                    cursor.execute(
                        "INSERT INTO entidades (id, codigo_igbe, nome) VALUES (?, ?, ?)",
                        (entidade_id, entidade_id, entidade_nome),  # Código IBGE é igual ao ID neste caso
                    )

        conn.commit()
        conn.close()
        print(f"{tabela.capitalize()} sincronizados com sucesso.")

    except requests.RequestException as e:
        print(f"Erro ao acessar a API {api_url}: {e}")
    except sqlite3.Error as e:
        print(f"Erro ao atualizar a tabela {tabela}: {e}")
    except ValueError as e:
        print(f"Erro de formatação na resposta da API {api_url}: {e}")

def atualizar_entidades(db_path):
    """Atualiza as tabelas de estados, cidades e entidades."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Banco de dados não encontrado no caminho: {db_path}")

    criar_tabelas(db_path)

    apis = {
        "estados": "https://api.rh247.com.br/230440023/app/sincronizacao/estados",
        "cidades": "https://api.rh247.com.br/230440023/app/sincronizacao/municipios",
        "entidades": "https://api.rh247.com.br/230440023/app/sincronizacao/entidades",
    }

    for tabela, api_url in apis.items():
        sincronizar_dados(api_url, tabela, db_path)

if __name__ == "__main__":
    DB_PATH = "banco_de_dados.db"
    atualizar_entidades(DB_PATH)
