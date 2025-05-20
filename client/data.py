URL = "http://server:5000"

predict_data = {
    "X": [[5.1, 3.5, 1.4, 0.2], [6.7, 3.1, 4.7, 1.5]]
}

names = ["rf_long", "svc_long", "rf_async", "svc_async"]

data = {
    "X": [[i % 10, (i * 2) % 7, (i * 3) % 5, (i * 4) % 3] for i in range(900000)],
    "y": [i % 2 for i in range(900000)]
}