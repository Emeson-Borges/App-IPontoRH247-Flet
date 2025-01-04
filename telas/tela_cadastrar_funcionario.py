import flet as ft
import hashlib
import sqlite3
import cv2
import base64
import time
from threading import Thread
import re

DB_PATH = "banco_de_dados.db"

# Função para processar e gerar o hash facial
def calcular_hash(rosto):
    """Calcula o hash SHA-256 do rosto processado."""
    rosto_em_bytes = rosto.tobytes()
    return hashlib.sha256(rosto_em_bytes).hexdigest()

def validar_cpf_formatado(cpf):
    """Valida o formato do CPF."""
    return re.match(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$", cpf) is not None

def formatar_cpf(cpf):
    """Formata o CPF conforme o usuário digita."""
    cpf = re.sub(r"\D", "", cpf)  # Remove qualquer caractere que não seja número
    if len(cpf) > 3:
        cpf = cpf[:3] + "." + cpf[3:]
    if len(cpf) > 7:
        cpf = cpf[:7] + "." + cpf[7:]
    if len(cpf) > 11:
        cpf = cpf[:11] + "-" + cpf[11:]
    return cpf[:14]  # Limita o CPF a 14 caracteres

def criar_tela_cadastrar_funcionario(page):
    # Variáveis para capturar a imagem facial
    rosto_capturado = None
    capturando_facial = False
    foto_base64 = None

    # Função para capturar o rosto do funcionário
    def capturar_rosto():
        nonlocal rosto_capturado, capturando_facial, foto_base64
        capturando_facial = True

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            emitir_alerta("Erro", "Não foi possível acessar a câmera.")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        start_time = time.time()

        while time.time() - start_time < 5:  # Captura durante 5 segundos
            ret, frame = cap.read()
            if ret:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

                for (x, y, w, h) in faces:
                    rosto_capturado = gray_frame[y:y + h, x:x + w]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Salva uma foto no formato base64
                _, buffer = cv2.imencode(".jpg", frame)
                foto_base64 = base64.b64encode(buffer).decode("utf-8")
                camera_feed.src_base64 = foto_base64
                page.update()

        capturando_facial = False
        cap.release()
        verificar_campos()

    # Função para verificar se todos os campos estão preenchidos
    def verificar_campos():
        salvar_btn.disabled = not (
            nome_input.value.strip() and
            validar_cpf_formatado(cpf_input.value.strip()) and
            matricula_input.value.strip() and
            entidade_input.value.strip() and
            rosto_capturado is not None
        )
        page.update()

    # Função para salvar o funcionário no banco de dados
    def salvar_funcionario():
        if not nome_input.value or not cpf_input.value or not matricula_input.value or not entidade_input.value:
            emitir_alerta("Erro", "Por favor, preencha todos os campos.")
            return

        if not validar_cpf_formatado(cpf_input.value):
            emitir_alerta("Erro", "CPF inválido. Use o formato 000.000.000-00.")
            return

        if rosto_capturado is None or foto_base64 is None:
            emitir_alerta("Erro", "Nenhum rosto foi capturado. Faça a prova de vida.")
            return

        try:
            rosto_hash = calcular_hash(rosto_capturado)
           
            _, buffer = cv2.imencode(".jpg", rosto_capturado)  # Salva apenas o rosto capturado
            foto_blob = buffer.tobytes()

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO funcionarios (nome, entidade_id, funcionario_id, cpf, hash_encoding, foto_base64, foto_blob)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    nome_input.value.strip(),
                    int(entidade_input.value.strip()),
                    int(matricula_input.value.strip()),
                    cpf_input.value.strip(),
                    rosto_hash,
                    foto_base64,
                    foto_blob,
                ),
            )

            conn.commit()
            conn.close()

            emitir_alerta("Sucesso", "Funcionário cadastrado com sucesso!")
            limpar_campos()
        except Exception as e:
            emitir_alerta("Erro", f"Ocorreu um erro: {e}")

    # Função para emitir alertas
    def emitir_alerta(titulo, mensagem):
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

    # Função para limpar os campos
    def limpar_campos():
        nome_input.value = ""
        cpf_input.value = ""
        matricula_input.value = ""
        entidade_input.value = ""
        camera_feed.src_base64 = ""
        salvar_btn.disabled = True
        page.update()

    # Componentes da tela
    nome_input = ft.TextField(label="Nome", width=300, on_change=lambda e: verificar_campos())
    cpf_input = ft.TextField(
        label="CPF (Formato: 000.000.000-00)",
        width=300,
        on_change=lambda e: (setattr(cpf_input, "value", formatar_cpf(cpf_input.value)), verificar_campos()),
    )
    matricula_input = ft.TextField(label="Matrícula", width=300, keyboard_type=ft.KeyboardType.NUMBER, on_change=lambda e: verificar_campos())
    entidade_input = ft.TextField(label="Entidade ID", width=300, keyboard_type=ft.KeyboardType.NUMBER, on_change=lambda e: verificar_campos())
    camera_feed = ft.Image(width=300, height=300)

    # Botões
    capturar_facial_btn = ft.ElevatedButton(
        text="Iniciar Prova de Vida",
        on_click=lambda e: Thread(target=capturar_rosto, daemon=True).start(),
        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
    )

    salvar_btn = ft.ElevatedButton(
        text="Salvar Funcionário",
        on_click=lambda e: salvar_funcionario(),
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE),
        disabled=True,  # Inicialmente desabilitado
    )

    voltar_btn = ft.TextButton(
        text="Voltar",
        on_click=lambda e: page.go("/administracao"),
        style=ft.ButtonStyle(color=ft.Colors.BLUE),
    )

    # Layout da tela com scroll
    layout = ft.Column(
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
        controls=[
            ft.Text(value="Cadastro de Funcionário", size=24, weight="bold"),
            nome_input,
            cpf_input,
            matricula_input,
            entidade_input,
            camera_feed,
            capturar_facial_btn,
            salvar_btn,
            voltar_btn,
        ],
    )

    # Retorna a tela como um View com scroll
    return ft.View(route="/cadastrar_funcionario", scroll="adaptive", controls=[layout])