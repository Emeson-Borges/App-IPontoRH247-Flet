import flet as ft

def criar_tela_administracao(page):
    # Função para voltar à tela principal
    def voltar(e):
        page.go("/")

    # Função para criar os cards com navegação
    def criar_card(icone, texto, subtitulo, rota):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(name=icone, size=30, color=ft.colors.BLUE),
                    ft.Text(value=texto, size=14, weight="bold", text_align="center"),
                    ft.Text(value=subtitulo, size=12, color="#666666", text_align="center"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            width=140,
            height=140,
            border_radius=15,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,
            padding=10,
            on_click=lambda e: page.go(rota),
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=2,
                color="#CCCCCC33",  # Cinza com 20% de opacidade
            ),
            # None,  # Remove sombra
        )

    # Layout da tela de administração com scroll
    layout = ft.Column(
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        scroll="adaptive",  # Adiciona scroll adaptativo
        controls=[
            # Cabeçalho com foto e informações
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text("A", size=24, weight="bold"),
                            bgcolor=ft.colors.BLUE,
                            radius=30,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value="PREFEITURA DEMONSTRAÇÃO",
                                    size=14,
                                    weight="bold",
                                    color="#666666",
                                ),
                                ft.Text(
                                    value="ABRAÃO FELIX DA SILVA CARVALHO",
                                    size=16,
                                    weight="bold",
                                    color="#333333",
                                ),
                                ft.Text(
                                    value="Matrícula: 00067141",
                                    size=14,
                                    color="#666666",
                                ),
                                ft.TextButton(
                                    text="Alterar Matrícula",
                                    on_click=lambda e: print("Alterar matrícula"),
                                    style=ft.ButtonStyle(color=ft.colors.BLUE),
                                ),
                            ],
                        ),
                    ],
                    spacing=15,
                ),
                padding=20,
                bgcolor="#F5F5F5",
                border_radius=10,
            ),

            # Card de competência
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text(value="Competência", size=14, color=ft.colors.WHITE),
                        ft.Text(value="OUT/2024", size=18, weight="bold", color=ft.colors.WHITE),
                        ft.Icon(name="calendar_today", color=ft.colors.WHITE, size=20),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=20,
                bgcolor=ft.colors.BLUE,
                border_radius=10,
            ),

            # Grid de cards
            ft.GridView(
                expand=False,
                runs_count=2,
                spacing=15,
                max_extent=160,
                controls=[
                    criar_card("autorenew", "Sincronizar", "Sincronizar pontos", "/sincronizar"),
                    criar_card("schedule", "Frequência Diária", "Veja seu espelho de ponto", "/frequencia"),
                    criar_card("event_note", "Lembretes", "Acesse seus lembretes", "/lembretes"),
                    criar_card("settings", "Entidade", "Configurar entidade", "/config_entidade"),
                    criar_card("supervised_user_circle", "Funcionários", "Cadastrar funcionários", "/cadastrar_funcionario"),
                    criar_card("fingerprint", "Ponto Facial", "Acesse o ponto facial", "/ponto_facial"),
                ],
            ),

            # Botão de voltar como um link azul
            ft.TextButton(
                text="Voltar",
                on_click=voltar,
                style=ft.ButtonStyle(
                    color=ft.colors.BLUE,
                    padding=ft.Padding(left=10, top=5, right=10, bottom=5),
                ),
            ),
        ],
    )

    # Retorna a tela como um View com scroll
    return ft.View(
        route="/administracao",
        scroll="adaptive",  # Adiciona scroll ao nível da view inteira
        controls=[layout],
    )
