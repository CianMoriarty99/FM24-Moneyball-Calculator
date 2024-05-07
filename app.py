# app.py

from flask import Flask, render_template, request, session
import pandas as pd
import numpy as np

def load_data(csv_file):
    df = pd.read_csv(csv_file)
    # Convert relevant columns to numeric
    df["Hdr %"] = df["Hdr %"].str.replace('%', '')
    df["Pas %"] = df["Pas %"].str.replace('%', '')
    df["Conv %"] = df["Conv %"].str.replace('%', '')
    numeric_columns = ["Tck/90", "Hdr %", "Blk/90", "Clr/90", "Int/90", "Pres C/90", "OP-KP/90", "Ch C/90", "Cr C/90", "Pr passes/90", "Pas %", "xA/90", "ShT/90", "Drb/90", "NP-xG/90", "Conv %"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    df["Hdr %"] = df["Hdr %"].astype(float) / 100.0
    df["Pas %"] = df["Pas %"].astype(float) / 100.0
    df["Conv %"] = df["Conv %"].astype(float) / 100.0
    df.fillna(0.0, inplace=True)

    return df


def get_target_values(df, target_name='TARGET'):
    target_row = df.loc[df['Name'] == target_name].drop(columns=['Name'])
    target_values = target_row.values.flatten()
    return target_values

def plot_comparisons(df, categories):
    for category in categories:
        best_index = df[category].idxmax()
        plt.figure()
        df.plot(x='Name', y=category, kind='bar') 
        plt.axhline(y=df.iloc[best_index][category], color='red', linestyle='--')
        plt.title(f'Best Player in {category}')
        plt.show()

def subtract_arrays(A, B):
    result = []
    for a, b in zip(A, B):
        result.append(((a - b) / b * 100) + 50 if b != 0 else 0)
    return result

def calculate_moneyball_number(row, targets):
    moneyball_number = sum(subtract_arrays(row, targets))
    return moneyball_number


app = Flask(__name__)
app.secret_key = 'your_secret_key'

uploaded_file = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['csv_file']
    position = request.form['position']
    data = load_data(uploaded_file)

    relevant_columns = [
        request.form['relevant_column_1'],
        request.form['relevant_column_2'],
        request.form['relevant_column_3'],
        request.form['relevant_column_4'],
        request.form['relevant_column_5']
    ]

    # Store the selected columns in session variables
    session['position'] = position
    session['relevant_columns'] = relevant_columns

    focused_data = data[["Name"] + relevant_columns]
    focused_targets = get_target_values(focused_data)

    scaled_data_df = focused_data.copy()
    scaled_data_df.drop(columns='Name', inplace=True)
    scaled_data_df['Moneyball Number'] = scaled_data_df.apply(calculate_moneyball_number, axis=1, args=(focused_targets,))
    scaled_data_df['Name'] = focused_data['Name']
    scaled_data_df['Position Compared'] = position

    scaled_data_df.sort_values(by='Moneyball Number', ascending=False, inplace=True)

    return render_template('result.html', data=scaled_data_df)

if __name__ == '__main__':
    app.run(debug=True)
