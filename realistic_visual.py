import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from models.predictive_control import AdaptivePredictiveController
import random

class RealisticTrafficSimulation:
    def __init__(self, df, controller):
        self.df = df
        self.controller = controller

        # --- Figure setup ---
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.ax.set_xlim(0, 120)
        self.ax.set_ylim(0, 100)
        self.ax.set_title("🚗 Adaptive Predictive Traffic Flow Simulation", fontsize=15, fontweight='bold')
        self.ax.set_facecolor("#dfe6e9")

        # --- Draw road ---
        self.ax.add_patch(plt.Rectangle((0, 20), 120, 60, color="#636e72"))  # main road
        for lane_y in [35, 50, 65]:
            self.ax.plot([0, 120], [lane_y, lane_y], 'w--', linewidth=2)  # lane markings

        # --- Traffic light ---
        self.light_color = "green"
        self.light = plt.Circle((10, 85), 4, color=self.light_color)
        self.ax.add_patch(self.light)
        self.ax.text(5, 92, "Signal", fontsize=10, fontweight="bold")

        # --- Vehicles (cars, trucks, bikes) ---
        self.cars = [{'x': random.randint(0, 100), 'y': 30, 'speed': random.uniform(1, 2.5)} for _ in range(8)]
        self.trucks = [{'x': random.randint(0, 100), 'y': 50, 'speed': random.uniform(0.8, 1.5)} for _ in range(5)]
        self.bikes = [{'x': random.randint(0, 100), 'y': 70, 'speed': random.uniform(1.5, 3)} for _ in range(7)]

        # --- Vehicle plots ---
        self.car_dots, = self.ax.plot([], [], 's', color='skyblue', markersize=10, label='Cars')
        self.truck_dots, = self.ax.plot([], [], 's', color='orange', markersize=12, label='Trucks')
        self.bike_dots, = self.ax.plot([], [], 'o', color='lime', markersize=6, label='Bikes')

        self.ax.legend(loc="upper right")

        # --- Simulation variables ---
        self.frame_index = 0
        self.speed_factor = 1.0

    def init(self):
        self.car_dots.set_data([], [])
        self.truck_dots.set_data([], [])
        self.bike_dots.set_data([], [])
        return self.car_dots, self.truck_dots, self.bike_dots, self.light

    def update(self, frame):
        row = self.df.iloc[self.frame_index % len(self.df)]
        features = [
            row['traffic_volume'], row['vehicle_count_cars'], row['vehicle_count_trucks'],
            row['vehicle_count_bikes'], row['weather_condition'], row['temperature'],
            row['humidity'], row['accident_reported'], row['signal_status']
        ]
        predicted_speed = self.controller.predict_speed(features)

        # --- Update signal based on data ---
        self.light_color = "red" if row['signal_status'] == "Red" else "green"
        self.light.set_color(self.light_color)

        # --- Adjust speed according to signal ---
        if self.light_color == "red":
            self.speed_factor = 0.3
        else:
            self.speed_factor = predicted_speed / 60

        # --- Move vehicles ---
        for car in self.cars:
            car['x'] += car['speed'] * self.speed_factor
            if car['x'] > 120: car['x'] = 0
        for truck in self.trucks:
            truck['x'] += truck['speed'] * self.speed_factor
            if truck['x'] > 120: truck['x'] = 0
        for bike in self.bikes:
            bike['x'] += bike['speed'] * self.speed_factor
            if bike['x'] > 120: bike['x'] = 0

        # --- Update positions ---
        self.car_dots.set_data([c['x'] for c in self.cars], [c['y'] for c in self.cars])
        self.truck_dots.set_data([t['x'] for t in self.trucks], [t['y'] for t in self.trucks])
        self.bike_dots.set_data([b['x'] for b in self.bikes], [b['y'] for b in self.bikes])

        self.ax.set_xlabel(f"Predicted Speed: {predicted_speed:.2f} km/h | Traffic Volume: {row['traffic_volume']} | Signal: {self.light_color.upper()}")
        self.frame_index += 1

        return self.car_dots, self.truck_dots, self.bike_dots, self.light

    def run(self):
        ani = animation.FuncAnimation(
            self.fig, self.update, init_func=self.init,
            frames=len(self.df), interval=300, blit=True, repeat=True
        )
        plt.show()


if __name__ == "__main__":
    df = pd.read_csv("data/traffic_data.csv")
    controller = AdaptivePredictiveController()
    controller.train(df)
    sim = RealisticTrafficSimulation(df, controller)
    sim.run()
