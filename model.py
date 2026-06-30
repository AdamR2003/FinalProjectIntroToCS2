import csv
import os

class FilamentModel:
    def __init__(self, filename="filament_data.csv"):
        self.filename = filename
        self.fields = ['Brand', 'Material', 'Color', 'ID', 'InitialWeight', 'CurrentWeight', 'LastDried']
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as f:
                csv.DictWriter(f, fieldnames=self.fields).writeheader()

    def get_data(self):
        with open(self.filename, 'r') as f:
            return list(csv.DictReader(f))

    def save_all(self, data_list):
        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(data_list)

    def add_data(self, row_data):
        with open(self.filename, 'a', newline='') as f:
            csv.DictWriter(f, fieldnames=self.fields).writerow(row_data)