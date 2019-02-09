import matplotlib.pyplot as plt

f = open("dataset/twitter_1000000.txt", "r")

xs = []
ys = []
for l in f:
    data = (l.split("\t")[1]).split(" ")
    xs.append(float(data[0]))
    ys.append(float(data[1]))

plt.scatter(xs,ys,s=1)

plt.title('Dataset preview')
plt.xlabel('x')
plt.ylabel('y')

plt.show()
