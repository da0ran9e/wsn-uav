#ifndef WSN_KMEANS_MODEL_H
#define WSN_KMEANS_MODEL_H

#include <vector>
#include <cmath>
#include <cstdint>

namespace ns3::wsn::uav {

struct Point {
    double x, y, z;
    uint32_t id;  // point identifier (node id, etc)

    Point() : x(0), y(0), z(0), id(0) {}
    Point(double x_, double y_, double z_, uint32_t id_ = 0)
        : x(x_), y(y_), z(z_), id(id_) {}

    double Distance(const Point& other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        double dz = z - other.z;
        return std::sqrt(dx * dx + dy * dy + dz * dz);
    }
};

class KMeansModel {
public:
    KMeansModel();
    virtual ~KMeansModel() = default;

    // Cluster points into k clusters
    // Returns: vector of cluster assignments (point index -> cluster index)
    std::vector<uint32_t> Cluster(const std::vector<Point>& points,
                                   uint32_t k,
                                   uint32_t maxIterations = 100);

    // Get cluster centers (centroids)
    const std::vector<Point>& GetCentroids() const { return m_centroids; }

    // Get cluster assignments
    const std::vector<uint32_t>& GetAssignments() const { return m_assignments; }

    // Get points in a specific cluster
    std::vector<Point> GetClusterPoints(const std::vector<Point>& points,
                                        uint32_t clusterIdx) const;

private:
    std::vector<Point> m_centroids;
    std::vector<uint32_t> m_assignments;

    void InitializeCentroids(const std::vector<Point>& points, uint32_t k);
    void AssignPointsToClusters(const std::vector<Point>& points);
    void UpdateCentroids(const std::vector<Point>& points);
    bool HasConverged(const std::vector<Point>& oldCentroids) const;
    double Distance(const Point& a, const Point& b) const;
};

}  // namespace ns3::wsn::uav

#endif  // WSN_KMEANS_MODEL_H
