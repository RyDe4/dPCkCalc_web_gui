from flask import Flask, render_template, request, redirect, url_for
from dPCkCalc import load_pc_data
import numpy as np
from matplotlib import pyplot as plt
import math

app = Flask(__name__)

last_uploaded = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        uploaded_file.save(uploaded_file.filename)
        global last_uploaded
        last_uploaded = uploaded_file.filename
    show_plot()
    return redirect(url_for('index'))

@app.route('/')
def show_plot():
    form = request.form
    patch_count = form["patch_num"]
    data = load_pc_data(int(patch_count), last_uploaded, coords=True)
    intra_total = 0
    flux_total = 0

    dpck_data = data[:, 1]
    intra_data = data[:, 2]
    flux_data = data[:, 3]
    indices = np.argsort(dpck_data)
    dpck_data = dpck_data[indices]
    intra_data = intra_data[indices]
    flux_data = flux_data[indices]

    percentile = None
    top_percent = False

    if percentile is not None:
        keep = math.ceil(percentile / 100 * len(dpck_data))
        if not top_percent:
            dpck_data_trimmed = dpck_data[0:keep]
            intra_data_trimmed = intra_data[0:keep]
            flux_data_trimmed = flux_data[0:keep]
        else:
            dpck_data_trimmed = dpck_data[len(dpck_data) - keep:len(dpck_data)]
            intra_data_trimmed = intra_data[len(dpck_data) - keep:len(dpck_data)]
            flux_data_trimmed = flux_data[len(dpck_data) - keep:len(dpck_data)]
    else:
        dpck_data_trimmed = dpck_data
        intra_data_trimmed = intra_data
        flux_data_trimmed = flux_data
    for i in range(len(dpck_data_trimmed)):
        if dpck_data_trimmed[i] > 0:
            intra_total = intra_total + intra_data_trimmed[i] / dpck_data_trimmed[i]
            flux_total = flux_total + flux_data_trimmed[i] / dpck_data_trimmed[i]
    intra_percent = intra_total / len(intra_data_trimmed)
    flux_percent = flux_total / len(flux_data_trimmed)
    connector_percent = 1 - flux_percent - intra_percent
    data_arr = np.array([intra_percent, flux_percent, connector_percent])
    labels = ["intra", "flux", "connector"]

    plt.pie(data_arr, labels=labels, autopct='%1.1f%%')
    plt.title("dPCk Fractions")
    plt.savefig("web_app/static/curr_im.png", bbox_inches='tight')

