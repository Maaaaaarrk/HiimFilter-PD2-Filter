import io.github.bonigarcia.wdm.WebDriverManager;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

public class Pd2Scraper {
    private static final String rootdir = System.getProperty("user.dir");
    private static final String dir = rootdir + "\\builder\\";


    private static Map<String, Double> scrapeHRMap(String url, WebDriver driver) {
        Map<String, Double> hrMap = new HashMap<>();
        try {
            driver.get(url);
            // Wait a bit for JS to load
            Thread.sleep(3000); // Adjust as needed
            String pageSource = driver.getPageSource();
            Document document = Jsoup.parse(pageSource);

            // Try to find the table or tbody
            Element table = document.select("table").first();
            if (table == null) {
                table = document.select("tbody").first();
            }
            Elements rows;
            if (table != null) {
                rows = table.select("tr");
            } else {
                // Fallback: select all tr elements
                rows = document.select("tr");
            }
            if (rows.isEmpty()) {
                System.err.println("No table or rows found on the page: " + url);
                return hrMap;
            }
            for (Element row : rows) {
                Elements cells = row.select("td");
                if (cells.size() >= 2) { // Assuming at least 2 columns: name, hr
                    String name = cells.get(0).text().trim();
                    // Sanitize the name: trim everything after "Rune" if present, and replace spaces with "_"
                    int runeIndex = name.indexOf("Rune");
                    if (runeIndex != -1) {
                        name = name.substring(0, runeIndex + 4);
                    }
                    if(name.contains("WIKI")){
                        name = name.replace("WIKI","");
                    }
                    name = name.trim();
                    name = name.replace(" ", "_");

                    String hrText = cells.get(1).text().trim();
                    // Extract the numeric HR value, e.g., from "2.15 HR"
                    String hrValueStr = hrText.replaceAll("[^0-9.]", "");
                    try {
                        double hrValue = Double.parseDouble(hrValueStr);
                        hrMap.put(name, hrValue);
                    } catch (NumberFormatException e) {
                        // Skip if not a valid number
                    }
                }
            }
        } catch (Exception e) {
            System.err.println("Error scraping " + url + ": " + e.getMessage());
        }
        return hrMap;
    }

    public static void main(String[] args) {
        String url = "https://pd2.tools/economy/runes";
        Map<String, Double> runeHRMap = new HashMap<>();
        Map<String, Double> pd2HRMAP = new HashMap<>();

        // TIMESTAMP_UPDATE
        String timestamp = "%WHITE%HR Values Last updated "+LocalDate.now().format(DateTimeFormatter.ofPattern("MMMM d yyyy"));

        // Setup ChromeDriver
        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless"); // Run in headless mode
        WebDriver driver = new ChromeDriver(options);

        try {
            // Scrape runes
            runeHRMap.putAll(scrapeHRMap("https://pd2.tools/economy/runes", driver));
            // Scrape currency
            pd2HRMAP.putAll(scrapeHRMap("https://pd2.tools/economy/currency", driver));
            // Scrape ubers
            pd2HRMAP.putAll(scrapeHRMap("https://pd2.tools/economy/ubers", driver));
        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        } finally {
            driver.quit();
        }
        // Process the template file and replace placeholders with RUNE HR values
        {
            System.out.println("Rune HR Update");
            String templatePath = dir + "07-Runes-ToolTip.template.filter";
            String outputPath = dir + "07-Runes-ToolTip.filter";
            try {
                String content = Files.readString(Paths.get(templatePath));

                //TIMESTAMP_UPDATE
                content = content.replace("TIMESTAMP_UPDATE", timestamp);
                for (Map.Entry<String, Double> entry : runeHRMap.entrySet()) {
                    if(content.contains(entry.getKey() + "_Value")) {
                        System.out.println(entry.getKey() + ": " + entry.getValue());
                        content = content.replace(entry.getKey() + "_Value", String.valueOf(entry.getValue()).replace(".0", ""));
                    }
                }
                Files.writeString(Paths.get(outputPath), content);
            } catch (Exception e) {
                System.err.println("Error processing template: " + e.getMessage());
            }
            System.out.println("---------");
        }

        // Uber Mats
        {
            System.out.println("Uber Mat HR Update");
            String templatePath = dir+"04-Ubermats.template.filter";
            String outputPath = dir+"04-Ubermats.filter";
            try {
                String content = Files.readString(Paths.get(templatePath));
                for (Map.Entry<String, Double> entry : pd2HRMAP.entrySet()) {
                    if(content.contains(entry.getKey() + "_Value")){
                    System.out.println(entry.getKey() + ": " + entry.getValue());
                    String hrVal = String.valueOf(entry.getValue());
                    if(hrVal.endsWith(".0")){
                        hrVal=   hrVal.replace(".0","");
                    }

                    if(hrVal.equals("0")){
                        content = content.replace(entry.getKey() + "_Value", "");
                    } else {
                        content = content.replace(entry.getKey() + "_Value", hrVal + " hr");
                    }
                    }
                }
                Files.writeString(Paths.get(outputPath), content);
            } catch (Exception e) {
                System.err.println("Error processing template: " + e.getMessage());
            }
            System.out.println("---------");
        }

        // PD2 Items
        {
            System.out.println("PD2 Items HR Update");
            String templatePath = dir+"03-PD2_items.template.filter";
            String outputPath = dir+"03-PD2_items.filter";
            try {
                String content = Files.readString(Paths.get(templatePath));
                for (Map.Entry<String, Double> entry : pd2HRMAP.entrySet()) {
                    if(content.contains(entry.getKey() + "_Value")){
                        System.out.println(entry.getKey() + ": " + entry.getValue());
                        String hrVal = String.valueOf(entry.getValue());
                        if(hrVal.endsWith(".0")){
                            hrVal=   hrVal.replace(".0","");
                        }

                        if(hrVal.equals("0")){
                            content = content.replace(entry.getKey() + "_Value", "");
                        } else {
                            content = content.replace(entry.getKey() + "_Value", "%TAN%HR Estimated Value Each%WHITE%: "+hrVal+"%CL%"+timestamp+"%CL%");
                        }
                    }
                }
                Files.writeString(Paths.get(outputPath), content);
            } catch (Exception e) {
                System.err.println("Error processing template: " + e.getMessage());
            }
            System.out.println("---------");
        }



        System.out.println("Full list");
        for (Map.Entry<String, Double> entry : pd2HRMAP.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }

    }
}
