import clustering as cl

k = 20
z = 10
m = 1 # I have implemented parameter m

clust = cl.ParallelStreamingClustering(k,z,cl.DEFAULT_ALPHA,cl.DEFAULT_BETA,cl.DEFAULT_ETA,m)

f = open("dataset/twitter_1000000.txt", "r")
try:
    for l in f:
        data = (l.split("\t")[1]).split(" ")
        clust.next((float(data[0]), float(data[1])))

    clust.end_batch_now()
    (clusters, r) = clust.get_clusters()
    print(str(r))
except:
    print("Error for line: " + l)

