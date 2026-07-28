"""
This file handles the read and writing operations to the filament_data.csv file.
Creator: Adam Romero
Last Updated: 07/28/2026
"""

import csv
import os
from typing import List, Dict, Any

class FilamentModel:
    """
    Manages the storage and retrieval of filament data from the csv file

    Attributes:
        filename (str): The name of the CSV file
        fields (list): The header names for the CSV columns
    """
    def __init__(self, filename="filament_data.csv") -> None:
        """Initializes the model and creates the CSV file if it doesn't exist.
        Args:
            filename (str): The CSV file path.
        """
        self.filename = filename
        self.fields = ['Brand', 'Material', 'Color', 'ID', 'InitialWeight', 'CurrentWeight', 'LastDried']
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as file:
                csv.DictWriter(file, fieldnames=self.fields).writeheader()

    def get_data(self) -> List[Dict[str, Any]]:
        """
        Reads the spool data from the CSV file

        Returns:
            List[Dict[str, Any]]: A list of spool record dictionaries.
        """
        with open(self.filename, 'r') as file:
            return list(csv.DictReader(file))

    def save_all(self, data_list: List[Dict[str, Any]]) -> None:
        """
        Replaces the CSV file with a provided list of dictionaries.

        Args:
            data_list (List[Dict[str, Any]]): Updated list of filament data
        """
        with open(self.filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(data_list)

    def add_data(self, row_data: Dict[str, Any]) -> None:
        """
        Appends a new spool record to the CSV file.

        Args:
            row_data (Dict[str, Any]): The new spool record dictionary.
        """
        with open(self.filename, 'a', newline='') as file:
            csv.DictWriter(file, fieldnames=self.fields).writerow(row_data)