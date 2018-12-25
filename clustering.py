import math

def norm2(x,y):
    return math.sqrt (x*x + y*y)

# Depending on the complexity of the distance, we can optionally add memoisation.
def distance(pt1, pt2):
    (x1,y1) = pt1
    (x2,y2) = pt2
    return norm2(x2-x1, y2-y1)

def max_index(arr):
    max_i = 0
    for i in range(len(arr)):
        if arr[i] > arr[max_i]:
            max_i = i
    return max_i

def all_interpoint_dists(pts):
    all_dists = set()
    for pt1 in pts:
        for pt2 in pts:
            all_dists.add(distance(pt1,pt2))
    return sorted(all_dists)

# OFFLINE ALGORITHM
# See 'Algorithms for Facility Location Problems with Outliers'

# Parameter 'unrestricted_centers' :
# set to 'False' for the original version of the algorithm (3-approx, centers among input points)
# set to 'True' for the modified version of the algorithm (4-approx, unrestricted centers)
def robust_clustering_with_radius(pts, k, p, optimal_r, unrestricted_centers):
    # Building the disks
    n = len(pts)
    Gr = 2*optimal_r if unrestricted_centers else optimal_r
    Er = 4*optimal_r if unrestricted_centers else 3*optimal_r
    G=[]
    E=[]
    for i in range(n):
        G_elts = []
        E_elts = []
        for j in range(n):
            dist = distance(pts[i],pts[j])
            if dist <= Gr :
                G_elts.append(j)
                E_elts.append(j)
            elif dist <= Er :
                E_elts.append(j)
        G.append(G_elts)
        E.append(E_elts)
    # Greedy algorithm
    covered = 0
    centers = []
    for i in range(k):
        weights = [len(G[j]) for j in range(n)]
        choosen = max_index(weights)
        centers.append(pts[choosen])
        for j in E[choosen]:
            Gj = G[j].copy()
            for k in Gj:
                G[k].remove(j)
            Ej = E[j].copy()
            for k in Ej:
                E[k].remove(j)
            covered += 1
    # Result
    if covered < p:
        return None
    return (centers,4*optimal_r if unrestricted_centers else 3*optimal_r)

# Parameter 'unrestricted_centers' :
# set to 'False' for the original version of the algorithm (3-approx, centers among input points)
# set to 'True' for the modified version of the algorithm (4-approx, unrestricted centers)
def robust_clustering(pts, k, p, unrestricted_centers):
    # Compute and sort all interpoint distances
    all_dists = all_interpoint_dists(pts)
    # Performs a binary search
    imin = 0
    imax = len(all_dists)-1
    last_sol = None
    while imax - imin >= 0:
        middle = imin + (imax-imin)//2
        (sol,r) = robust_clustering_with_radius(pts, k, p, all_dists[middle], unrestricted_centers)
        if sol == None:
            imin = middle+1
        else:
            last_sol = (sol, r)
            imax = middle-1
    return last_sol

# STREAMING ALGORITHM
# See 'Streaming algorithms for k-center clustering with outliers and with anonymity'

class Not_initialized(Exception):
    pass

class StreamingClustering:

    def __init__(self,k,z,alpha,beta,eta,initial_r_factor):
        # Check that the parameters satisfy prerequisites
        assert eta >= 2*alpha + beta
        assert eta*alpha >= eta + 2*(alpha**2) + 2*beta
        assert beta >= 2*alpha
        assert eta >= 4*alpha

        self.k = k
        self.z = z
        self.alpha = alpha
        self.beta = beta
        self.eta = eta
        self.irf = initial_r_factor

        self.__init_step = True
        self.__init_pts = []
        self.__r = 0

        self.__cur_batch = 0
        self.__free_points = []
        self.__clusters = []
        self.__clusters_support = []
        self.__offline_clusters = []

    def next(self, pt):
        if self.__init_step:
            self.__init_pts.append(pt)
            if len(self.__init_pts) >= self.k + self.z + 1:
                self.__init_step = False
                # Set r
                min_dist = all_interpoint_dists(self.__init_pts)[0]
                self.__r = self.irf * min_dist / 2
                # Treat points that we already have
                for p in self.__init_pts:
                    self.next(p)
        else:
            self.__cur_batch += 1
            self.__free_points.append(pt)
            if self.__cur_batch >= self.k * self.z:
                self.end_batch_now()

    def __pt_is_in_cluster(self, pt):
        r = self.eta * self.__r
        for p in self.__clusters:
            if distance(p,pt) <= r:
                return True
        return False

    def __clusters_conflict(self, i, j):
        for pt1 in self.__clusters_support[i]:
            for pt2 in self.__clusters_support[j]:
                if distance(pt1, pt2) <= 2 * self.alpha * self.__r:
                    return True
        return False

    def __perform_batch_step(self):
        while True:
            r = self.beta * self.__r
            loop_step1 = True
            while loop_step1:
                loop_step1 = False
                #1: Drop free points that are not free anymore
                self.__free_points = [x for x in self.__free_points if self.__pt_is_in_cluster(x) == False]
                #2: Make a new cluster if necessary
                for pt1 in self.__free_points:
                    support = []
                    for pt2 in self.__free_points:
                        if distance(pt1,pt2) <= r:
                            support.append(pt2)
                        if len(support) >= self.z + 1:
                            break
                    if len(support) >= self.z + 1:
                        self.__clusters.append(pt1)
                        self.__clusters_support.append(support)
                        loop_step1 = True
                        break

            #3: Check feasability and proceed to with offline clustering
            l = len(self.__clusters)
            n = len(self.__free_points)
            r = self.eta * self.__r / 4
            if l <= self.k and n <= (self.k - l + 1)*self.z:
                (res,_) = robust_clustering_with_radius(self.__free_points, self.k-l, n-self.z, r, True)
                self.__offline_clusters = res
                if res!=None:
                    return
            #4: Otherwise: increase radius, remove useless clusters
            self.__r *= self.alpha
            i = 0
            while i < len(self.__clusters):
                j = i+1
                while j < len(self.__clusters):
                    if self.__clusters_conflict(i,j):
                        self.__clusters.pop(j)
                        self.__clusters_support.pop(j)
                    j += 1
                i += 1

    def end_batch_now(self):
        if self.__init_step:
            raise Not_initialized()
        self.__cur_batch = 0
        self.__perform_batch_step()

    def get_clusters(self):
        return (self.__clusters + self.__offline_clusters, self.eta * self.__r)

class ParallelStreamingClustering:
    
    def __init__(self,k,z,alpha,beta,eta,m):
        self.__instances = []
        for i in range(m):
            irf = math.pow(alpha, (i+1)/m - 1)
            self.__instances.append(StreamingClustering(k,z,alpha,beta,eta,irf))

    def next(self, pt):
        for inst in self.__instances:
            inst.next(pt)

    def end_batch_now(self):
        for inst in self.__instances:
            inst.end_batch_now()

    def get_clusters(self):
        min_r = math.inf
        min_clusters = None
        for inst in self.__instances:
            (clusters, r) = inst.get_clusters()
            if r < min_r:
                min_r = r
                min_clusters = clusters
        return (min_clusters, min_r)
    
DEFAULT_ALPHA=4
DEFAULT_BETA=8
DEFAULT_ETA=16
