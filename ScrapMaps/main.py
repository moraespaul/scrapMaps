import flet as ft
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv

driver = None
results = []


def setup_selenium():
    global driver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    service = Service()  # Substitua pelo caminho correto
    driver = webdriver.Chrome(service=service, options=options)


def scroll_in_container(page,container, pause_time=2):
    status.value = f"Coletando informações..."
    page.update()
    last_height = driver.execute_script("return arguments[0].scrollHeight", container)
    while True:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(pause_time)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == last_height:
            break
        last_height = new_height


def scrap_data(page):
    global results

    try:
        parent_elements = driver.find_elements(By.CSS_SELECTOR, ".UaQhfb.fontBodyMedium")
        results = []

        for parent in parent_elements:
            try:
                name = parent.find_element(By.CSS_SELECTOR, ".qBF1Pd.fontHeadlineSmall").text
                address = parent.find_element(By.CLASS_NAME, "UsdlK").text
                results.append((name, address))
                result_table.rows.append(
                    ft.DataRow(cells=[ft.DataCell(ft.Text(name)), ft.DataCell(ft.Text(address))])
                )
                page.update()
                time.sleep(0.5)

            except Exception:
                pass

        status.value = f"Coleta finalizada: {len(results)} resultados."
        page.update()

    except Exception as e:
        status.value = f"Erro durante o scraping: {e}"
        page.update()
    finally:
        driver.quit()
    status.value = f"Coleta finalizada: {len(results)} resultados."
    page.update()


def pesquisar(page, cidade):
    if not cidade:
        status.value = "Por favor, insira o nome de uma cidade!"
        page.update()
        return

    status.value = f"Buscando chaveiros em {cidade}..."
    page.update()

    setup_selenium()

    url = f"https://www.google.com/maps/search/chaveiros+in+{cidade}"
    driver.get(url)
    time.sleep(5)
    status.value = f"Carregando arquivos Necessários.."
    page.update()
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[class="m6QErb DxyBCb kA9KIf dS8AEf XiKgde ecceSd"]')
    scroll_in_container(page, scrollable_div)

    scrap_data(page)


def save_csv(page, file_picker_result, cidade):
    global results

    if not results:
        status.value = "Nenhum dado para salvar!"
        page.update()
        return

    if not file_picker_result.path:  # Verifica se o usuário selecionou um caminho
        status.value = "Operação de salvamento cancelada!"
        page.update()
        return

    # Verifica se o arquivo tem a extensão .csv e, se não, adiciona
    if not file_picker_result.path.endswith(".csv"):
        file_picker_result.path += ".csv"

    # Salva o arquivo CSV no caminho selecionado
    with open(file_picker_result.path, mode="w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["Nome do Chaveiro", "Endereço"])
        writer.writerows(results)

    status.value = f"Dados salvos como {file_picker_result.path}"
    page.update()

    result_table.rows.clear()
    if cidade is not None:  # Verifica se 'cidade' não é None antes de acessar 'value'
        cidade.value = ""
        page.update()


def main(page: ft.Page):
    global result_table, status

    #     # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 700
    page.window.width = 490
    page.window.resizable = True
    #     # page.window.top = 300
    #     # page.window.left = 500

    page.title = "Dovale Chaves - ScrapMaps"
    page.bgcolor = "#070042"

    cidade = ft.TextField(
        col=7,
        label="Cidade",
        color=ft.colors.WHITE,
        bgcolor=ft.colors.BLACK,
        border_color="#789AF4",
        tooltip="Insira a cidade para buscar chaveiros.",
        on_submit=lambda e: pesquisar(page, cidade.value)
    )

    pesquisar_btn = ft.ElevatedButton(
        col=5,
        text="Pesquisar",
        icon=ft.icons.SEARCH,
        on_click=lambda _: pesquisar(page, cidade.value)
    )

    salvar_btn = ft.ElevatedButton(
        text="Salvar CSV",
        icon=ft.icons.SAVE,
        on_click=lambda _: file_picker.save_file()
    )

    status = ft.Text(value="Status: Aguardando consulta...", color=ft.colors.WHITE)

    result_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nome do Chaveiro")),
            ft.DataColumn(ft.Text("Endereço"))
        ],
        rows=[]
    )

    scrollable_table = ft.ListView(
        controls=[result_table],
        height=400,  # Define a altura visível
        spacing=5,  # Espaçamento entre itens (opcional)
    )
    file_picker = ft.FilePicker(
        on_result=lambda e: save_csv(page, e, cidade)  # Passa o evento do FilePicker para a função de salvar
    )

    page.add(
        ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            value="Dovale - ScrapMaps",
                            size=30,
                            color=ft.colors.WHITE)
                    ]
                ),
                ft.ResponsiveRow(
                    columns=12,
                    controls=[cidade, pesquisar_btn]
                ),


                status,
                # result_table,
                scrollable_table,
                salvar_btn,
                file_picker,
            ]
        )
    )

    cidade.focus()


ft.app(target=main)



