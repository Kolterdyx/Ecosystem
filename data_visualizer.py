import matplotlib.pyplot as plt
from itertools import count
from matplotlib.animation import FuncAnimation
import pandas as pd


plt.style.use('dark_background')

index = count()

	
def animate(i):
    data = pd.read_csv('data.csv')
    x = data['step']
    y1 = data['cell_ammount']
    y2 = data['asexcell_ammount']
    total = data["total_ammount"]

    plt.cla()

    plt.subplot(2,2,1)
    plt.plot(x, y1, label='Sexual cell ammount', color="#C8C800")
    plt.subplot(2,2,2)
    plt.plot(x, y2, label='Asexual cell ammount', color="#FF64FF")
    plt.subplot(2,2,3)
    plt.plot(x, y1, label='Sexual cell ammount', color="#C8C800")
    plt.plot(x, y2, label='Asexual cell ammount', color="#FF64FF")
    plt.subplot(2,2,4)
    plt.plot(x, total, label='Total ammount', color="#999999")

    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=500)

plt.tight_layout()
plt.show()
