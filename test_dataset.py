import clustering as cl
import time
import matplotlib.pyplot as plt

optimal_radius_ub = 42

k = 20

ms = [1,3,5]
zs = [10,20,30,40,50]

ts = []
ratios = []

for m in ms:
    m_ts = []
    m_ratios = []

    for z in zs:

        clust = cl.ParallelStreamingClustering(k,z,cl.DEFAULT_ALPHA,cl.DEFAULT_BETA,cl.DEFAULT_ETA,m)
        f = open("dataset/twitter_1000000.txt", "r")

        timer = time.time()
        for l in f:
            data = (l.split("\t")[1]).split(" ")
            x = float(data[0])
            y = float(data[1])
            clust.next((x, y))
        clust.end_batch_now()
        timer = time.time() - timer

        (clusters, r) = clust.get_clusters()
        ratio = r/optimal_radius_ub
        m_ts.append(timer)
        m_ratios.append(ratio)

        print("For z={z} and m={m}:".format(z=z,m=m))
        print("r={r}".format(r=r))
        print("ratio={ratio}".format(ratio=ratio))
        print("factor_guaranteed={g}".format(g=clust.approx_factor_guaranteed()))
        print("time={t}".format(t=timer))
        print("")

    ts.append(m_ts)
    ratios.append(m_ratios)

f1 = plt.figure(1)
plt.axis([min(zs), max(zs), 1, max(map(max, ratios))])
for i in range(len(ratios)):
    plt.plot(zs, ratios[i])

f2 = plt.figure(2)
plt.axis([min(zs), max(zs), 0, max(map(max, ts))])
for i in range(len(ts)):
    plt.plot(zs, ts[i])

plt.show()
