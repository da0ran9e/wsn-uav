#include "kmeans-model.h"
#include <algorithm>
#include <random>
#include <limits>

namespace ns3::wsn::uav {

KMeansModel::KMeansModel() {}

std::vector<uint32_t> KMeansModel::Cluster(const std::vector<Point>& points,
                                           uint32_t k,
                                           uint32_t maxIterations) {
    if (points.empty() || k == 0) {
        return {};
    }

    // Ensure k doesn't exceed number of points
    k = std::min(k, (uint32_t)points.size());

    InitializeCentroids(points, k);
    m_assignments.resize(points.size());

    for (uint32_t iter = 0; iter < maxIterations; iter++) {
        std::vector<Point> oldCentroids = m_centroids;

        AssignPointsToClusters(points);
        UpdateCentroids(points);

        if (HasConverged(oldCentroids)) {
            break;
        }
    }

    return m_assignments;
}

void KMeansModel::InitializeCentroids(const std::vector<Point>& points, uint32_t k) {
    m_centroids.clear();
    m_centroids.reserve(k);

    // Initialize with k random points from the dataset
    std::vector<uint32_t> indices(points.size());
    for (uint32_t i = 0; i < points.size(); i++) {
        indices[i] = i;
    }

    std::random_device rd;
    std::mt19937 gen(rd());
    std::shuffle(indices.begin(), indices.end(), gen);

    for (uint32_t i = 0; i < k; i++) {
        m_centroids.push_back(points[indices[i]]);
    }
}

void KMeansModel::AssignPointsToClusters(const std::vector<Point>& points) {
    for (size_t i = 0; i < points.size(); i++) {
        double minDist = std::numeric_limits<double>::max();
        uint32_t closestCluster = 0;

        for (size_t j = 0; j < m_centroids.size(); j++) {
            double dist = Distance(points[i], m_centroids[j]);
            if (dist < minDist) {
                minDist = dist;
                closestCluster = j;
            }
        }

        m_assignments[i] = closestCluster;
    }
}

void KMeansModel::UpdateCentroids(const std::vector<Point>& points) {
    for (size_t j = 0; j < m_centroids.size(); j++) {
        double sumX = 0.0, sumY = 0.0, sumZ = 0.0;
        uint32_t count = 0;

        for (size_t i = 0; i < points.size(); i++) {
            if (m_assignments[i] == j) {
                sumX += points[i].x;
                sumY += points[i].y;
                sumZ += points[i].z;
                count++;
            }
        }

        if (count > 0) {
            m_centroids[j].x = sumX / count;
            m_centroids[j].y = sumY / count;
            m_centroids[j].z = sumZ / count;
        }
    }
}

bool KMeansModel::HasConverged(const std::vector<Point>& oldCentroids) const {
    const double threshold = 1e-6;
    for (size_t i = 0; i < m_centroids.size(); i++) {
        if (Distance(m_centroids[i], oldCentroids[i]) > threshold) {
            return false;
        }
    }
    return true;
}

double KMeansModel::Distance(const Point& a, const Point& b) const {
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    double dz = b.z - a.z;
    return std::sqrt(dx * dx + dy * dy + dz * dz);
}

std::vector<Point> KMeansModel::GetClusterPoints(const std::vector<Point>& points,
                                                 uint32_t clusterIdx) const {
    std::vector<Point> result;
    for (size_t i = 0; i < points.size(); i++) {
        if (m_assignments[i] == clusterIdx) {
            result.push_back(points[i]);
        }
    }
    return result;
}

}  // namespace ns3::wsn::uav
