from pdb import set_trace
from os import listdir
from os.path import isfile, join
import glob
import numpy as np
import math

class DataAnalysis:

    def __init__(self) -> None:
        self.path_to_infer = './teste/infer.py'
        self.path_to_train = './teste/train.py'
        self.path_to_predicted_landmarks = "./teste/results/landmarks/test/" #"./results/landmarks/test/"
        self.path_to_original_landmarks = "./landmarks_from_ct/"

    def get_landmarks(self, read_file: str) -> dict:
        try:
            landmark_number = 0
            landmarks = {}
            with open(read_file, 'r') as file:
                for row in file:
                    row = row.split()
                    landmarks[landmark_number] = list(map(float, row))
                    landmark_number += 1
                return landmarks
        except Exception as ex:
            print(ex)

    def calculate_euclidean_distance(self, original_landmarks: dict, predicted_landmarks: dict) -> float:
        result = []
        for key, value in original_landmarks.items():
            ol_x, ol_y, ol_z = value
            pl_x, pl_y, pl_z = predicted_landmarks[key]
            result.append(math.dist([ol_x, ol_y, ol_z], [pl_x, pl_y, pl_z]))
        return result

    def calculate_mae(self, euclidean_distance: list) -> float:
        return np.mean(euclidean_distance)

    def infer_data(self):
        result = {}
        with open(self.path_to_infer, 'r') as file:
            for line in file:
                line = line.strip('\n').replace(' ', '').split("=")
                if line[0] in ['predict_mode', 'num_random_init', 'max_test_steps', 'box_size', 'eigvec_per']:
                    line[1] = line[1].split('#')[0]
                    result[line[0]] = float(line[1])
                    if line[0] == 'predict_mode':
                        break
        return result


    def train_data(self):
        result = {}
        with open(self.path_to_train, 'r') as file:
            for line in file:
                line = line.strip('\n').replace(' ', '').split("=")
                if line[0] in ['shape_model_file']:
                    line[1] = line[1].strip("'").strip(" ").split('/')[-1]
                    result[line[0]] = line[1].split('/')[-1]
        return result


    def data_analysis(self):
        predicted_landmarks_files = glob.glob(self.path_to_predicted_landmarks + "*.txt")
        result = {}
        try:
            for predicted_file in predicted_landmarks_files:
                file_name = predicted_file.split('/')[-1]

                original_file_name = self.path_to_original_landmarks + file_name
                original_landmarks = self.get_landmarks(original_file_name)
                predicted_landmarks = self.get_landmarks(predicted_file)

                euclidean_distance = self.calculate_euclidean_distance(original_landmarks, predicted_landmarks)

                result[file_name] = {
                    'euclidean_distance': euclidean_distance,
                    'mae': self.calculate_mae(euclidean_distance)
                }
                #print(f'{file_name} -> Euclidean Distance: {euclidean_distance} MAE: {mae}')
            network_data = self.infer_data()
            network_data.update(self.train_data())

            return  network_data, result
        except Exception as ex:
            print(ex)