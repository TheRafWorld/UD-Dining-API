import json
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch a headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Load the Caesar Rodney page
        await page.goto("https://udel.campusdish.com/LocationsAndMenus/CaesarRodneyFreshFoodCompany", timeout=60000)
        
        # Wait for the menu sections to render
        try:
            await page.wait_for_selector("h3", timeout=15000)
        except:
            pass
        
        # Run your exact DOM extraction logic inside the page
        menu_data = await page.evaluate("""
            () => {
                let elements = Array.from(document.querySelectorAll('h3, div[aria-label="Recipe"] h4, [class*="Recipe"] h4, .menu-item-name'))
                  .filter(el => el.getBoundingClientRect().height > 0);

                let categorizedMenu = {};
                let currentCategory = "Uncategorized";

                let globalIgnoreList = [
                  "Trabant Food Court", "CR Fresh Food Company", "Pencader Dining Hall", "Whitney Kitchen", 
                  "The Nest in Morris Library Commons", "Flip Kitchen", "Snap Pizza at Trabant LRR", 
                  "Market Place In Perkins", "Academy Cookies in Perkins", "The Den by Dennys", "Dunkin Donuts", 
                  "La Casa Pasta at Perkins Local Restaurant Row", "Gore P.O.D. Express", "Smith Hall Coffee Shop", 
                  "Einstein Bros. Bagels", "The Rolling Rooster", "Chick-fil-A", "Halal Shack", "Claymont Steak Shop", 
                  "Stomping Grounds", "IFC Sushi", "Market Place", "The Juice Joint 2.0", "P.O.D. Market at Harrington", 
                  "Figure 8 POD", "Pencader POD Market"
                ];

                elements.forEach(el => {
                  let rawText = el.innerText || el.textContent;
                  if (!rawText) return;
                  
                  let text = rawText.trim();
                  let tag = el.tagName.toLowerCase();

                  if (tag === 'h3') {
                    if (!globalIgnoreList.includes(text)) {
                      currentCategory = text;
                      if (!categorizedMenu[currentCategory]) {
                        categorizedMenu[currentCategory] = [];
                      }
                    }
                  } else {
                    if (!categorizedMenu[currentCategory]) {
                      categorizedMenu[currentCategory] = [];
                    }
                    if (text.length > 0 && !categorizedMenu[currentCategory].includes(text)) {
                      categorizedMenu[currentCategory].push(text);
                    }
                  }
                });

                // Filter out empty categories
                let cleanMenu = {};
                for (let key in categorizedMenu) {
                  if (categorizedMenu[key].length > 0) {
                    cleanMenu[key] = categorizedMenu[key];
                  }
                }
                return cleanMenu;
            }
        """)
        
        await browser.close()
        
        # Save to cr-menu.json
        with open("cr-menu.json", "w") as f:
            json.dump(menu_data, f, indent=2)
        print("Menu successfully updated:", menu_data)

asyncio.run(main())