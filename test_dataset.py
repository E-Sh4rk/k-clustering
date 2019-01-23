import clustering as cl

k = 20
z = 10 # TODO: Algo outputs greater result (138>114) when z=50. Investigate it. Not true when m=3 (55<72).
m = 1  # I have implemented parameter m

clust = cl.ParallelStreamingClustering(k,z,cl.DEFAULT_ALPHA,cl.DEFAULT_BETA,cl.DEFAULT_ETA,m)

f = open("dataset/twitter_1000000.txt", "r")
min_x = 0
max_x = 0
min_y = 0
max_y = 0
try:
    for l in f:
        data = (l.split("\t")[1]).split(" ")
        x = float(data[0])
        y = float(data[1])
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
        clust.next((x, y))

    clust.end_batch_now()
    (clusters, r) = clust.get_clusters()
    print("Output radius: " + str(r))
    print("Top-left point: (" + str(min_x) + ", " + str(min_y) + ")")
    print("Bottom-right point: (" + str(max_x) + ", " + str(max_y) + ")")
except:
    print("Error for line: " + l)

