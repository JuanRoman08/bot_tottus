import pandas as pd
from playwright.async_api import async_playwright
import asyncio
import os
from datetime import datetime

# Crear carpetas si no existen
os.makedirs("logs", exist_ok=True)
os.makedirs("excels", exist_ok=True)

# Función para registrar logs
def registrar_log(mensaje):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    log_file = f"logs/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{now} - INFO - {mensaje}\n")

# Función principal de scraping
async def buscar_productos():
    search_term_raw = input("\n🔍 Ingresa el producto que deseas buscar: ").strip()
    search_term = search_term_raw.replace(" ", "%20")
    url = f"https://www.tottus.com.pe/tottus-pe/buscar?Ntt={search_term}"
    print(f"🌐 Buscando en: {url}\n")
    registrar_log(f"Iniciando búsqueda de: {search_term}")

    products = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)

        try:
            await page.wait_for_selector("a[data-pod='catalyst-pod']", timeout=10000)
        except:
            print("❌ No se encontraron productos.")
            await browser.close()
            return

        items = await page.query_selector_all("a[data-pod='catalyst-pod']")

        for item in items:
            try:
                title = await item.query_selector("b[id^='testId-pod-displaySubTitle']")
                nombre = await title.inner_text() if title else "Sin nombre"

                precio_internet_tag = await item.query_selector("li[data-internet-price] span")
                precio_internet = await precio_internet_tag.inner_text() if precio_internet_tag else "-"

                precio_cmr_tag = await item.query_selector("li[data-cmr-price] span")
                precio_cmr = await precio_cmr_tag.inner_text() if precio_cmr_tag else "-"

                precio_normal_tag = await item.query_selector("li[data-normal-price] span")
                precio_normal = await precio_normal_tag.inner_text() if precio_normal_tag else "-"

                img_tag = await item.query_selector("img")
                imagen_url = await img_tag.get_attribute("src") if img_tag else "Sin imagen"

                href = await item.get_attribute("href")
                link = "https://www.tottus.com.pe" + href if href else "Sin enlace"

                products.append({
                    "Búsqueda": search_term_raw,
                    "Nombre": nombre.strip(),
                    "💻 Precio Internet": precio_internet,
                    "💳 Precio CMR": precio_cmr,
                    "🏷️ Precio Normal": precio_normal,
                    "📎 Enlace": link,
                    "🖼️ Imagen": imagen_url
                })

                print(f"✅ {nombre} - {precio_internet}")
                registrar_log(f"Producto OK: {nombre} - {precio_internet}")
            except Exception as e:
                print(f"❌ Error con producto: {e}")
                registrar_log(f"ERROR: {e}")
                continue

        await browser.close()

    # Guardar Excel en carpeta con nombre personalizado
    if products:
        safe_term = search_term_raw.lower().replace(" ", "_").replace("%", "")
        base_name = f"excels/productos_{safe_term}"
        filename = f"{base_name}.xlsx"
        counter = 1
        while os.path.exists(filename):
            filename = f"{base_name}_{counter}.xlsx"
            counter += 1

        df = pd.DataFrame(products)
        df.to_excel(filename, index=False)
        print(f"📄 Archivo {filename} generado correctamente.")
        registrar_log(f"Archivo {filename} generado correctamente.")
    else:
        print("⚠️ No se extrajo ningún dato.")
        registrar_log("⚠️ No se extrajo ningún dato.")

# Menú de consola
def menu():
    while True:
        print("\n========= MENÚ PRINCIPAL =========")
        print("1. 🔍 Buscar productos y exportar a Excel")
        print("2. 📂 Ver archivos Excel generados")
        print("3. 📜 Ver logs")
        print("4. 🚪 Salir")
        opcion = input("Selecciona una opción (1-4): ")

        if opcion == "1":
            asyncio.run(buscar_productos())
        elif opcion == "2":
            print("\n📄 Archivos Excel disponibles:")
            for file in os.listdir("excels"):
                if file.endswith(".xlsx"):
                    print(f" - {file}")
        elif opcion == "3":
            print("\n📜 Logs disponibles:")
            for file in os.listdir("logs"):
                if file.startswith("log_") and file.endswith(".log"):
                    print(f" - {file}")
        elif opcion == "4":
            print("👋 ¡Hasta pronto!")
            break
        else:
            print("⚠️ Opción no válida. Intenta nuevamente.")

# Ejecutar menú
if __name__ == "__main__":
    menu()
