import os
import yaml
import requests
import rust_module
from bs4 import BeautifulSoup
from datetime import datetime
from calendar import monthrange

launchTime = datetime.now()
launchTimeFormat = launchTime.strftime("%d-%m-%Y-%H-%M-%S")

# ”settings.yml” parsing
with open("settings.yml") as file: 
    settings = yaml.safe_load(file)
    
offset = settings["offset"]
OFFSET_BOOL = offset["offset"]
OFFSET_VALUE = offset["value"] if OFFSET_BOOL else 1
releaseDate = settings["release_date"]
RELEASEDATE_BOOL = releaseDate["release_date"]
RELEASEDATE_YEARS = releaseDate["years"]
WEBSITES_LIST = settings["websites_list"]
EXCEPTIONS_LIST = settings["exceptions_list"]

OUTPUT_FOLDER_NAME = "output"
OUTPUTFILE_PATH = f"{OUTPUT_FOLDER_NAME}/output-{launchTimeFormat}.yml"
OUTPUTFILE_COMPLETE_PATH = f"{OUTPUT_FOLDER_NAME}/output-{launchTimeFormat}-complete.yml"
OUTPUTFILE_PATTERN = {
    "url": {},
    "login": {},
    "password": {}
}

YEAR_RANGE = launchTime.month if RELEASEDATE_BOOL and len(RELEASEDATE_YEARS) == 1 and launchTime.year in RELEASEDATE_YEARS else 12 
 

def progress_bar(
    doing_something: str, 
    current: int, 
    total: int
) -> None:
    """
    This function prints a progress bar with the specified doing_something, current, and total values.
    """
    percent = 100 * current/total
    round_percent = round(percent)
    bar = round_percent*"█"+(100-round_percent)*"#"

    print(f"\r{doing_something} {bar} \033[1;36m[{percent:.2f}%]\033[0m",
          end="\r")


def process_url(url: str) -> None:
    """
    This function sends a GET request to the specified URL and parses the HTML content.
    If the status code of the response is not 404, it extracts the release date from the HTML content.
    If the release date is within the specified range or is a specified year, it extracts the website text and calls the 'parse' function from the 'rust_module' to process the text.
    If the result is not an empty string, it calls the 'write_output' function to write the parsed data to the output file.
    """
    page = requests.get(url)

    if page.status_code!= 404:
        soup = BeautifulSoup(page.text, "html.parser")
        release_date = int(soup.select_one("time").get_text("\n", strip=True)[-4:])
        if RELEASEDATE_BOOL or release_date in RELEASEDATE_YEARS:
            website_text = [sentence for sentence in soup.stripped_strings]
            result = rust_module.parse(EXCEPTIONS_LIST, website_text)
            if result[0]!= "": write_output(url, result)


def write_output(url: str, data: list[str]) -> None:
    """
    This function writes the parsed data to the output file.
    """
    with open(OUTPUTFILE_PATH, "r") as file:
        output_data = yaml.safe_load(file)

    output_data["url"][write_output.counter] = url
    output_data["login"][write_output.counter] = data[0]
    output_data["password"][write_output.counter] = data[1] 

    with open(OUTPUTFILE_PATH, "w") as file:
        yaml.dump(output_data, file)
    
    write_output.counter += 1


def main():
    if not os.path.exists(OUTPUT_FOLDER_NAME):
        os.mkdir(OUTPUT_FOLDER_NAME)

    with open(OUTPUTFILE_PATH, "w") as file:
        yaml.dump(OUTPUTFILE_PATTERN, file)

    total_days = sum([monthrange(2020, month)[1] for month in range(1, YEAR_RANGE+1)])

    write_output.counter = 1

    counter = 1
    for month in range(1, YEAR_RANGE+1):
        for day in range(1, monthrange(2020, month)[1]+1):
            for value in range(OFFSET_VALUE):
                url_list = [url+f"-{month:02}-{day:02}-{value}" if value > 0 
                            else url+f"-{month:02}-{day:02}" 
                            for url in WEBSITES_LIST]
                
                for url in url_list: process_url(url)

                progress_bar("Parsing...", counter, total_days*OFFSET_VALUE)
                counter += 1

    os.rename(OUTPUTFILE_PATH, OUTPUTFILE_COMPLETE_PATH)
    print(f"\n\n\033[1;32mSuccessfull complete!\033[0m --> {OUTPUTFILE_COMPLETE_PATH}")


if __name__ == "__main__":
    main()