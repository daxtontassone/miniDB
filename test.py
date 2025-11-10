import requests
from bs4 import BeautifulSoup

def reveal_message(doc_url):
    """
    Pulls a google doc table with (x, char, y) entries
    and prints out the hidden block text message.
    """

    # download the doc html
    resp = requests.get(doc_url)
    html_text = resp.text   # save the raw html as a string using BeautifulSoup
    soup = BeautifulSoup(html_text, "html.parser")  # parse into a tree we can search

    # get all table rows (each row has x, char, y)
    # in html, <tr> is table row
    rows = soup.find_all("tr")
    coords = []  # coords hold tuples like (x, y, char)

    # loop through rows
    for row in rows:
        # in html, <td> is table data and <th> is table header
        cols = row.find_all(["td", "th"])
        if len(cols) < 3:
            # skip rows that don’t have all 3 pieces
            continue

        try:
            # pull out the text for x, y, and the character
            x_str = cols[0].get_text().strip()
            y_str = cols[2].get_text().strip()
            char = cols[1].get_text().strip()

            # convert x and y to integers
            x = int(x_str)
            y = int(y_str)
        except:
            # skip rows with bad formatting
            continue

        if char != "":
            # only keep rows with an actual character
            coords.append((x, y, char))

    # get overall grid size
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = (max_x - min_x) + 1   # number of columns
    height = (max_y - min_y) + 1  # number of rows

    # build an empty grid (2D list filled with spaces)
    grid = []
    for _ in range(height):
        grid.append([" "] * width)

    # drop each character into its spot
    for (x, y, symbol) in coords:
        grid[y - min_y][x - min_x] = symbol

    # print the rows from top to bottom
    # y=0 is the "bottom", so we flip vertically
    for row in grid[::-1]:
        print("".join(row))


if __name__ == "__main__":
    # example document link
    url = "https://docs.google.com/document/d/e/2PACX-1vRPzbNQcx5UriHSbZ-9vmsTow_R6RRe7eyAU60xIF9Dlz-vaHiHNO2TKgDi7jy4ZpTpNqM7EvEcfr_p/pub"
    reveal_message(url)
