import flet as ft
import sqlite3
import requests
import os


def verificar_conexao_internet():
    """Verifica se há conexão com a internet."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


def criar_tela_sincronizar_batidas(page: ft.Page, db_path: str):
    if not os.path.exists(db_path):
        raise ValueError(f"Banco de dados não encontrado no caminho: {db_path}")

    registros = []
    menu_aberto = False

    # Elementos da tela
    filtro_matricula = ft.TextField(label="Matrícula", width=250)
    filtro_data_inicio = ft.TextField(label="Data início (YYYY-MM-DD)", width=250)
    filtro_data_fim = ft.TextField(label="Data fim (YYYY-MM-DD)", width=250)
    status_text = ft.Text("Nenhum registro encontrado.", size=18, color=ft.Colors.RED)
    batidas_list = ft.ListView(expand=True, spacing=10)
    menu_lateral = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(value="Filtros", size=24, weight="bold"),
                filtro_matricula,
                filtro_data_inicio,
                filtro_data_fim,
                ft.ElevatedButton(
                    text="Aplicar Filtros",
                    on_click=lambda e: aplicar_filtros(),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
                ),
            ],
            spacing=10,
        ),
        width=300,
        bgcolor=ft.Colors.WHITE,
        padding=15,
        visible=False,
    )

    def carregar_registros():
        """Carrega registros do banco de dados com base nos filtros."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT id, data_ponto, funcionario_vinculo_id FROM ponto_final WHERE sincronizado = 0"
        filtros = []

        if filtro_matricula.value.strip():
            query += " AND funcionario_vinculo_id = ?"
            filtros.append(filtro_matricula.value.strip())

        if filtro_data_inicio.value.strip():
            query += " AND date(data_ponto) >= ?"
            filtros.append(filtro_data_inicio.value.strip())

        if filtro_data_fim.value.strip():
            query += " AND date(data_ponto) <= ?"
            filtros.append(filtro_data_fim.value.strip())

        cursor.execute(query, filtros)
        resultado = cursor.fetchall()
        conn.close()

        registros.clear()
        batidas_list.controls.clear()

        if resultado:
            for reg in resultado:
                registros.append(reg)
                batidas_list.controls.append(
                    ft.Checkbox(label=f"ID: {reg[0]}, Data: {reg[1]}, Funcionário ID: {reg[2]}", value=False)
                )
            status_text.value = f"{len(resultado)} registros encontrados."
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = "Nenhum registro encontrado."
            status_text.color = ft.Colors.RED

        page.update()

    def aplicar_filtros():
        """Aplica os filtros e atualiza a lista."""
        carregar_registros()

    def sincronizar_batidas(e):
        """Sincroniza as batidas selecionadas."""
        if not verificar_conexao_internet():
            emitir_alerta("Erro", "Sem conexão com a internet. Conecte-se ao Wi-Fi para sincronizar.")
            return

        registros_selecionados = [
            registros[idx] for idx, checkbox in enumerate(batidas_list.controls) if checkbox.value
        ]

        if not registros_selecionados:
            emitir_alerta("Aviso", "Nenhum registro selecionado para sincronizar.")
            return

        # Simulação de sincronização
        for reg in registros_selecionados:
            print(f"Sincronizando registro: {reg}")

        emitir_alerta("Sucesso", "Registros sincronizados com sucesso!")
        carregar_registros()

    def emitir_alerta(titulo, mensagem):
        """Exibe um alerta com título e mensagem."""
        def fechar_dialog(e):
            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Text(mensagem),
            actions=[ft.TextButton("OK", on_click=fechar_dialog)],
        )
        page.dialog.open = True
        page.update()

    def toggle_menu(e):
        """Alterna a visibilidade do menu lateral."""
        nonlocal menu_aberto
        menu_aberto = not menu_aberto
        menu_lateral.visible = menu_aberto
        page.update()

    carregar_registros()

    return ft.View(
        route="/sincronizar_batidas",
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(icon=ft.icons.MENU, on_click=toggle_menu),
                    ft.Text("Sincronizar Batidas", size=24, weight="bold"),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Row(
                controls=[
                    menu_lateral,
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                status_text,
                                batidas_list,
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            text="Sincronizar",
                                            on_click=sincronizar_batidas,
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE
                                            ),
                                        ),
                                        ft.ElevatedButton(
                                            text="Voltar",
                                            on_click=lambda e: page.go("/administracao"),
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE
                                            ),
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                ),
                            ],
                            spacing=10,
                        ),
                        expand=True,
                    ),
                ],
                expand=True,
            ),
        ],
    )
