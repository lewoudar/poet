import parsel
import httpx


def find_relevant_packages(package: str) -> dict[str, str]:
    packages = {}
    response = httpx.get('https://pypi.org/search/', params={'q': package})
    if response.status_code >= 400:
        return packages

    selector = parsel.Selector(text=response.text)
    h3_list = selector.xpath('//h3[@class="package-snippet__title"]')
    for h3 in h3_list:
        version = h3.xpath('span[@class="package-snippet__version"]/text()').get()
        name = h3.xpath('span[@class="package-snippet__name"]/text()').get()
        packages[name] = version

    return packages
