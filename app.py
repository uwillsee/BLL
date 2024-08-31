from flask import Flask, render_template
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd

app = Flask(__name__)

# Загрузка данных
data = pd.read_csv('data.csv')

def create_plot(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_url

@app.route('/')
def index():
    # Визуализация 1: Распределение книг по полу автора
    gender_distribution = data['Gender'].value_counts()
    fig1 = plt.figure()
    gender_distribution.plot(kind='bar')
    plt.title('Распределение книг по полу автора')
    plt.xlabel('Пол')
    plt.ylabel('Количество книг')
    plot_url1 = create_plot(fig1)

    # Визуализация 2: Количество книг, приобретенных за годы
    books_acquired_by_year = data['DateAcquired'].value_counts().sort_index()
    fig2 = plt.figure()
    books_acquired_by_year.plot(kind='line', marker='o')
    plt.title('Количество книг, приобретенных за годы')
    plt.xlabel('Год приобретения')
    plt.ylabel('Количество книг')
    plt.grid(True)
    plot_url2 = create_plot(fig2)

    # Визуализация 3: Распределение книг по жанру
    classification_distribution = data['Classification'].value_counts()
    fig3 = plt.figure()
    classification_distribution.plot(kind='bar')
    plt.title('Распределение книг по жанру')
    plt.xlabel('Жанр')
    plt.ylabel('Количество книг')
    plt.xticks(rotation=45, ha='right')
    plot_url3 = create_plot(fig3)

    # Визуализация 4: Распределение страниц в книгах
    fig4 = plt.figure()
    plt.hist(data['Pages'].dropna(), bins=20, color='skyblue', edgecolor='black')
    plt.title('Распределение страниц в книгах')
    plt.xlabel('Количество страниц')
    plt.ylabel('Количество книг')
    plt.grid(True)
    plot_url4 = create_plot(fig4)

    return render_template('index.html', plot_url1=plot_url1, plot_url2=plot_url2, plot_url3=plot_url3, plot_url4=plot_url4)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
