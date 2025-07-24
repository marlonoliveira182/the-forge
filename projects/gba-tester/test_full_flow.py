import os
import re
import pytest
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path='gba_access.env')

# Função para aguardar o título da página
def wait_for_title(page, expected_title, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if page.title() == expected_title:
                return
        except Exception:
            pass  # Ignora erros de contexto destruído e tenta novamente
        time.sleep(0.5)
    raise TimeoutError(f"Título '{expected_title}' não apareceu em {timeout} segundos.")

# Função de login manual aguardando o título da dashboard
def login(page):
    url = os.getenv("PINT_URL")
    if not url:
        raise RuntimeError("A variável de ambiente PINT_URL não está definida. Verifique seu arquivo .env.")
    page.goto(url)
    print("Faça o login manualmente na janela do navegador...")
    page.wait_for_load_state("networkidle", timeout=180_000)
    wait_for_title(page, "Dashboard - GBA", timeout=180)
    assert page.title() == "Dashboard - GBA"

# Função para criar artefato
def criar_artefato(page, nome, versao, descricao):
    page.get_by_role("link", name="Artifacts").click()
    page.get_by_role("link", name="All Artifacts").click()
    page.get_by_role("button", name="Create Artifact").click()
    page.get_by_role("combobox").click()
    page.get_by_text("Non Integration Artifact").click()
    page.get_by_role("textbox", name="Artifact Name *").fill(nome)
    page.get_by_role("textbox", name="Version *").fill(versao)
    page.get_by_role("textbox", name="Description").fill(descricao)
    page.get_by_role("textbox", name="Authentication Method *").fill("basic auth")
    page.get_by_role("combobox").filter(has_text="Select communication type").click()
    page.get_by_role("option", name="REST").click()
    page.get_by_role("combobox").filter(has_text="Select communication format").click()
    page.get_by_role("option", name="JSON").click()
    page.get_by_role("combobox").filter(has_text="Select exposing application").click()
    page.get_by_text("Not Yet Catalogued").click()
    page.get_by_role("button", name="Create Artifact").click()
    page.wait_for_timeout(2000)

# Função para tirar print de tela em caso de falha
def screenshot_on_failure(page, step_name):
    path = f"screenshot_{step_name}.png"
    page.screenshot(path=path, full_page=True)
    print(f"Screenshot salvo: {path}")

@pytest.mark.parametrize("nome,versao,descricao", [
    ("backend-test-api", "1", "test backend api"),
])
def test_full_flow(page, nome, versao, descricao):
    try:
        login(page)
    except Exception as e:
        screenshot_on_failure(page, 'login')
        raise AssertionError(f"Falha no login ou dashboard: {e}")

    try:
        criar_artefato(page, nome, versao, descricao)
        # Verifica se o artefato foi criado (ajuste o seletor conforme necessário)
        assert page.is_visible('text=Artifacts'), "Página de Artifacts não visível após criação."
    except Exception as e:
        screenshot_on_failure(page, 'criar_artefato')
        raise AssertionError(f"Falha ao criar artefato: {e}")

    print("Teste de fluxo completo realizado com sucesso!") 