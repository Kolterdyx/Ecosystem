
import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')

x_vals = []
y_vals = []

index = count()


def animate(i):
    data = pd.read_csv('data.csv')
    x = data['step']
    y1 = data['cell_ammount']
    y2 = data['asexcell_ammount']

    plt.cla()

    plt.plot(x, y1, label='Sexual cell ammount')
    plt.plot(x, y2, label='Asexual cell ammount')

    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=1000)

plt.tight_layout()
plt.show()
