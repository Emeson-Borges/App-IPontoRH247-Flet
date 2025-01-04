import sqlite3
import flet as ft
import os

def criar_tabela_configuracao(db_path):
    """Cria a tabela de entidades configuradas se não existir."""
    tabela = """
        CREATE TABLE IF NOT EXISTS entidades_configuradas (
            id INTEGER PRIMARY KEY NOT NULL,
            entidade_id INTEGER NOT NULL,
            estado_id INTEGER NOT NULL,
            cidade_id INTEGER NOT NULL,
            codigo_igbe VARCHAR(200) NOT NULL,
            name VARCHAR(200) NOT NULL
        );
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(tabela)
    conn.commit()
    conn.close()

def carregar_opcoes(db_path, tabela):
    """Carrega as opções de estado, cidade ou entidade do banco de dados."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, nome FROM {tabela}")
    opcoes = cursor.fetchall()
    conn.close()
    return opcoes

def salvar_configuracao(db_path, estado_id, cidade_id, entidade_id):
    """Salva a configuração selecionada na tabela de entidades configuradas."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM entidades_configuradas")  # Remove a configuração anterior

    # Insere a nova configuração
    cursor.execute(
        """
        INSERT INTO entidades_configuradas (entidade_id, estado_id, cidade_id, codigo_igbe, name)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            entidade_id,
            estado_id,
            cidade_id,
            f"{cidade_id}-{estado_id}",  # Código IBGE formatado
            "Configuração Atual"
        ),
    )
    conn.commit()
    conn.close()

def criar_tela_config_entidade(page: ft.Page, db_path: str):
    if not os.path.exists(db_path):
        raise ValueError(f"Banco de dados não encontrado no caminho: {db_path}")

    criar_tabela_configuracao(db_path)

    estados = carregar_opcoes(db_path, "estados")
    cidades = []
    entidades = []

    estado_dropdown = ft.Dropdown(
        label="Selecione o Estado",
        options=[],
        on_change=lambda e: carregar_cidades(),
        border_radius=10,
        border_color=ft.Colors.BLUE,
        filled=True,
    )
    cidade_dropdown = ft.Dropdown(
        label="Selecione o Município",
        options=[],
        on_change=lambda e: carregar_entidades(),
        border_radius=10,
        border_color=ft.Colors.BLUE,
        filled=True,
    )
    entidade_dropdown = ft.Dropdown(
        label="Selecione a Entidade",
        options=[],
        border_radius=10,
        border_color=ft.Colors.BLUE,
        filled=True,
    )

    status_text = ft.Text("", color=ft.Colors.RED, size=16)

    def carregar_estados():
        """Carrega os estados no dropdown."""
        estado_dropdown.options = [ft.dropdown.Option(str(estado[0]), estado[1]) for estado in estados]
        page.update()

    def carregar_cidades():
        """Carrega os municípios no dropdown com base no estado selecionado."""
        nonlocal cidades
        estado_id = estado_dropdown.value
        if not estado_id:
            return
        cidades = carregar_opcoes(db_path, "cidades")
        cidade_dropdown.options = [
            ft.dropdown.Option(str(cidade[0]), cidade[1]) for cidade in cidades if str(cidade[0]).startswith(estado_id)
        ]
        page.update()

    def carregar_entidades():
        """Carrega as entidades no dropdown com base no município selecionado."""
        nonlocal entidades
        cidade_id = cidade_dropdown.value
        if not cidade_id:
            return
        entidades = carregar_opcoes(db_path, "entidades")
        entidade_dropdown.options = [
            ft.dropdown.Option(str(entidade[0]), entidade[1]) for entidade in entidades
        ]
        page.update()

    def salvar_configuracao_app(e):
        """Salva a configuração selecionada no banco de dados."""
        estado_id = estado_dropdown.value
        cidade_id = cidade_dropdown.value
        entidade_id = entidade_dropdown.value

        if not (estado_id and cidade_id and entidade_id):
            status_text.value = "Por favor, selecione todas as opções antes de salvar."
            page.update()
            return

        salvar_configuracao(db_path, int(estado_id), int(cidade_id), int(entidade_id))
        status_text.value = "Configuração salva com sucesso!"
        status_text.color = ft.Colors.GREEN
        page.update()

    carregar_estados()

    return ft.View(
        route="/config_entidade",
        controls=[
            ft.Column(
                controls=[
                    ft.Image(src="/assets/rh247_azul.png", width=200),  # Logo RH247 no topo
                    ft.Text("Configuração de Entidade", size=28, weight="bold", text_align="center"),
                    estado_dropdown,
                    cidade_dropdown,
                    entidade_dropdown,
                    ft.ElevatedButton(
                        text="Salvar Configuração",
                        on_click=salvar_configuracao_app,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
                    ),
                    status_text,
                    ft.ElevatedButton(
                        text="Voltar",
                        on_click=lambda e: page.go("/administracao"),
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=25,  # Espaçamento entre os elementos
            )
        ],
    )
