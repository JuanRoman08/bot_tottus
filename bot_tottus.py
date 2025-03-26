import pandas as pd
from playwright.async_api import async_playwright
import asyncio
import os
import logging
from datetime import datetime

# Configurar logs
log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(filename=log_filename, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    search_term = input("🔍 Ingresa el producto que deseas buscar: ").strip().replace(" ", "%20")
    url = f"https://www.tottus.com.pe/tottus-pe/buscar?Ntt={search_term}"
    print(f"🌐 Buscando en: {url}\n")
    logging.info(f"Iniciando búsqueda de: {search_term}")

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
            logging.warning("No se encontraron productos.")
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
                    "Nombre": nombre.strip(),
                    "💻 Precio Internet": precio_internet,
                    "💳 Precio CMR": precio_cmr,
                    "🏷️ Precio Normal": precio_normal,
                    "📎 Enlace": link,
                    "🖼️ Imagen": imagen_url
                })

                print(f"✅ {nombre} - {precio_internet}")
                logging.info(f"Producto OK: {nombre} - {precio_internet}")

            except Exception as e:
                print(f"❌ Error con producto: {e}")
                logging.error(f"Error con producto: {e}")
                continue

        await browser.close()

    # Guardar en Excel sin sobrescribir
    if products:
        base_name = "productos_tottus_completo"
        filename = f"{base_name}.xlsx"
        counter = 1

        while os.path.exists(filename):
            try:
                with open(filename, 'r'):
                    filename = f"{base_name}_{counter}.xlsx"
                    counter += 1
            except PermissionError:
                filename = f"{base_name}_{counter}.xlsx"
                counter += 1

        df = pd.DataFrame(products)
        df.to_excel(filename, index=False)
        print(f"📄 Archivo {filename} generado correctamente.")
        logging.info(f"Archivo {filename} guardado con {len(products)} productos.")
    else:
        print("⚠️ No se extrajo ningún dato.")
        logging.warning("No se extrajo ningún dato.")

# Ejecutar
asyncio.run(main())
