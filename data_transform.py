import re
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_rotten_tomatoes_html(movie_url):
    try:
        response = requests.get(movie_url)

        if response.status_code == 200:
            #html_raw = remove_blank_lines(response.text) 
            html_raw = response.text
            return html_raw
        else:
            print("Failed to fetch data from Rotten Tomatoes. Status code:", response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None
    

""" def remove_blank_lines(text):
    if text:
        cleaned_text = re.sub(r'\n\s*\n', '\n', text)  # Remove blank lines
        return cleaned_text
    return None """


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


def get_movie_info(html_code):
    movie_info = {}

    soup = BeautifulSoup(html_code, 'html.parser')

    info_list = soup.find('ul', id='info')

    for info_item in info_list.find_all('li', {'data-qa': 'movie-info-item'}):
        label = info_item.find('b', {'data-qa': 'movie-info-item-label'}).text.strip()
        value = info_item.find('span', {'data-qa': 'movie-info-item-value'}).text.strip()
        movie_info[label] = value

    return pd.DataFrame([movie_info])

def soure_reader():
    movie_titles = list()
    with open("source.txt", 'r') as file:
        for line in file:
            movie_titles.append(line.strip()) 
    return movie_titles


def main():
    movie_titles = soure_reader()
    reviews_df = pd.DataFrame()

    for movie in movie_titles:
        i = 0
        url_for_comments = f"https://www.rottentomatoes.com/m/{movie}/reviews"
        url_for_the_movie_info = f"https://www.rottentomatoes.com/m/{movie}"

        html_code_comments = get_rotten_tomatoes_html(url_for_comments)
        html_code_movie_info = get_rotten_tomatoes_html(url_for_the_movie_info)

        comments_df = get_comments(html_code_comments, movie)
        movie_info_df = get_movie_info(html_code_movie_info)

        for index, row in comments_df.iterrows():
            if row['Movie'] == movie:
                i+=1

        movie_info_df = pd.concat([movie_info_df] * i, ignore_index=True)
        comments_df = comments_df.join(movie_info_df)
        reviews_df = pd.concat([reviews_df, comments_df], ignore_index=True)

    print(reviews_df)
    reviews_df.to_excel("reviews.xlsx", index=False)


if __name__ == "__main__":
    main()
