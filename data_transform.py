import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_rotten_tomatoes_html(movie_url):
    try:
        response = requests.get(movie_url)

        if response.status_code == 200:
            html_raw = remove_blank_lines(response.text) 
            return html_raw
        else:
            print("Failed to fetch data from Rotten Tomatoes. Status code:", response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
    

def remove_blank_lines(text):
    if text:
        cleaned_text = re.sub(r'\n\s*\n', '\n', text)  # Remove blank lines
        return cleaned_text
    return None


def get_comments(html_code, movie_title):
    soup = BeautifulSoup(html_code, 'html.parser')

    review_rows = soup.find_all('div', class_='review-row')

    data = []  

    for review in review_rows:
        critic_name = review.find('a', class_='display-name').text.strip()
        publication = review.find('a', class_='publication').text.strip()
        review_text = review.find('p', class_='review-text').text.strip()
        review_date = review.find('span', attrs={'data-qa': 'review-date'}).text.strip()

        data.append({
            'Movie' : movie_title,
            'Critic Name': critic_name,
            'Publication': publication,
            'Review Text': review_text,
            'Review Date': review_date
        })

    return pd.DataFrame(data)


def main():
    movie_titles = list()
    with open("source.txt", 'r') as file:
        for line in file:
            movie_titles.append(line.strip()) 
    
    reviews_df = pd.DataFrame()

    for movie in movie_titles:
        movie_url = f"https://www.rottentomatoes.com/m/{movie}/reviews"
        html_code = get_rotten_tomatoes_html(movie_url)
        df = get_comments(html_code, movie)

        reviews_df = pd.concat([reviews_df, df], ignore_index=True)

    print(reviews_df)
    
    reviews_df.to_excel("reviews.xlsx", index=False)


if __name__ == "__main__":
    main()
