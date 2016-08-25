package net.junaraki.annobase.util.graph;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Set;

/**
 * This class provides Dijkstra's algorithm. It solves the single-source shortest-paths problem on a
 * weighted, directed graph G = (V, E) for the case in which all edge weights are nonnegative.
 * 
 * @author Jun Araki
 */
public class DijkstraShortestPath {

  /**
   * Returns the shortest path from the given source vertex to the given destination vertex using
   * the Dijkstra algorithm. This method returns the shortest path as a list of vertexes. An empty
   * list means that the two vertices are the same.
   * 
   * @param graph
   * @param src
   * @param dest
   * @return
   */
  public static <V, E> List<V> getShortestPath(Graph<V, E> graph, V src, V dest) {
    List<V> path = new ArrayList<V>();
    if (src == null || dest == null || src.equals(dest)) {
      return path;
    }

    // Initialization
    Map<V, V> prevMap = new HashMap<V, V>();
    Map<V, Double> distMap = new HashMap<V, Double>();
    for (V vertex : graph.getVertices()) {
      distMap.put(vertex, Double.POSITIVE_INFINITY);
    }
    distMap.put(src, 0.0d);

    Set<V> visited = new HashSet<V>();
    PriorityQueue<V> queue = new PriorityQueue<V>();
    queue.add(src);

    while (!queue.isEmpty()) {
      V u = queue.poll();
      visited.add(u);

      for (V v : graph.getAdjacentVertices(u)) {
        double distance = distMap.get(u) + 1.0d;
        if (distance < distMap.get(v) && !visited.contains(v)) {
          distMap.put(v, distance);
          prevMap.put(v, u);
          queue.add(v);
        }
      }
    }

    if (!prevMap.containsKey(dest)) {
      // No path is found, which means the two vertices are disconnected
      return null;
    }

    path.add(dest);
    V v = dest;
    while (prevMap.containsKey(v)) {
      path.add(prevMap.get(v));
      v = prevMap.get(v);
    }
    Collections.reverse(path);

    return path;
  }

}
