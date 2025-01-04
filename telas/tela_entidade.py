def criar_tela_selecao(page: ft.Page):
    estados = ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia"]  # Lista de estados
    municipios = {
        "São Paulo": ["São Paulo", "Campinas", "Santos"],
        "Rio de Janeiro": ["Rio de Janeiro", "Niterói", "Petrópolis"],
        "Minas Gerais": ["Belo Horizonte", "Uberlândia", "Contagem"],
        "Bahia": ["Salvador", "Feira de Santana", "Vitória da Conquista"]
    }
    entidades = {
        "São Paulo": ["Entidade SP1", "Entidade SP2"],
        "Rio de Janeiro": ["Entidade RJ1", "Entidade RJ2"],
        "Minas Gerais": ["Entidade MG1", "Entidade MG2"],
        "Bahia": ["Entidade BA1", "Entidade BA2"]
    }

    # Componentes visuais
    estado_dropdown = ft.Dropdown(
        label="Estado",
        options=[ft.dropdown.Option(estado) for estado in estados],
        on_change=lambda e: atualizar_municipios(e.control.value),
        width=300
    )
    municipio_dropdown = ft.Dropdown(label="Município", width=300)
    entidade_dropdown = ft.Dropdown(label="Entidade", width=300)

    status_text = ft.Text("Por favor, preencha todas as seleções.", size=16, color=ft.colors.RED)

    # Atualizar os municípios com base no estado selecionado
    def atualizar_municipios(estado_selecionado):
        municipio_dropdown.options = [
            ft.dropdown.Option(municipio) for municipio in municipios.get(estado_selecionado, [])
        ]
        municipio_dropdown.value = None
        entidade_dropdown.options = []  # Limpa entidades ao mudar o estado
        entidade_dropdown.value = None
        page.update()

    # Atualizar as entidades com base no município selecionado
    def atualizar_entidades(e):
        estado_selecionado = estado_dropdown.value
        if estado_selecionado and municipio_dropdown.value:
            entidade_dropdown.options = [
                ft.dropdown.Option(entidade) for entidade in entidades.get(estado_selecionado, [])
            ]
            entidade_dropdown.value = None
        page.update()

    # Validação da seleção
    def validar_selecao():
        if not estado_dropdown.value or not municipio_dropdown.value or not entidade_dropdown.value:
            status_text.value = "Erro: Todas as seleções são obrigatórias."
            status_text.color = ft.colors.RED
        else:
            status_text.value = f"Seleção concluída: {estado_dropdown.value} / {municipio_dropdown.value} / {entidade_dropdown.value}"
            status_text.color = ft.colors.GREEN
            # Aqui você pode redirecionar para outra tela após a seleção
            page.go("/")  # Redireciona para a tela principal
        page.update()

    # Layout
    return ft.View(
        route="/selecao",
        controls=[
            ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Text("Selecione o Estado, Município e Entidade", size=20, weight="bold"),
                    estado_dropdown,
                    municipio_dropdown,
                    entidade_dropdown,
                    ft.ElevatedButton(
                        text="Confirmar Seleção",
                        on_click=lambda e: validar_selecao(),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE,
                            color=ft.colors.WHITE,
                            padding=ft.Padding(20, 10, 20, 10),
                        ),
                    ),
                    status_text,
                ],
            )
        ],
    )

def main(page: ft.Page):
    # Configurações da página
    page.title = "RH247"
    page.window_width = 360
    page.window_height = 640
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Navegar para as telas
    def navegar(rota):
        if rota == "/selecao":
            page.views.clear()
            page.views.append(criar_tela_selecao(page))  # Tela inicial
        elif rota == "/":
            page.views.clear()
            page.views.append(
                ft.View(
                    route="/",
                    controls=[  # A tela principal
                        ft.Text("Tela Principal", size=20, weight="bold"),
                        ft.ElevatedButton(
                            text="Ir para Seleção",
                            on_click=lambda e: page.go("/selecao"),
                        ),
                    ],
                )
            )
        elif rota == "/login":
            page.views.append(criar_tela_login(page))
        elif rota == "/administracao":
            page.views.append(criar_tela_administracao(page))
        elif rota == "/registro_ponto":
            page.views.append(criar_tela_registro_ponto(page, DB_PATH))  # Vai para a tela de registro de ponto
        elif rota == "/prova_vida":
            page.views.append(criar_tela_prova_vida(page, DB_PATH))  # Passa o caminho do banco de dados
        page.update()

    # Configurar rotas
    page.on_route_change = lambda e: navegar(page.route)
    page.go("/selecao")  # Inicializa na tela de seleção

ft.app(target=main)
