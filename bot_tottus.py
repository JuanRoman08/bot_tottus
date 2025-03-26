import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def main():
    url = "https://www.tottus.com.pe/tottus-pe/buscar?Ntt=leche%20gloria"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url)
        await page.wait_for_selector("a.jsx-4014752167.pod-link", timeout=60000)

        productos = await page.query_selector_all("a.jsx-4014752167.pod-link")

        lista_productos = []

        for producto in productos:
            # Nombre del producto
            nombre_element = await producto.query_selector("b.pod-subTitle")
            nombre = await nombre_element.inner_text() if nombre_element else "Sin nombre"

            # Precio del producto (buscar solo el de internet)
            precio_element = await producto.query_selector("li[data-internet-price] span")
            precio = await precio_element.inner_text() if precio_element else "Sin precio"

            print(f"✅ {nombre} - {precio}")

            lista_productos.append({
                "Nombre": nombre.strip(),
                "Precio": precio.strip()
            })

        # Guardar en Excel
        df = pd.DataFrame(lista_productos)
        df.to_excel("productos_tottus.xlsx", index=False)
        print("📄 Archivo productos_tottus.xlsx generado correctamente.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
