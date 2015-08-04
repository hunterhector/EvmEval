package net.junaraki.annobase.util.graph;

import java.util.Set;

/**
 * This interface provides a general graph.
 * 
 * @author Jun Araki
 *
 * @param <V> type of vertices
 * @param <E> type of edges
 */
public interface Graph<V, E> {

  /**
   * Returns all vertices in this graph.
   * 
   * @return
   */
  public Set<V> getVertices();

  /**
   * Returns vertices adjacent to the given vertex.
   * 
   * @param vertex
   * @return
   */
  public Set<V> getAdjacentVertices(V vertex);

  /**
   * Adds the given vertex to this graph.
   * 
   * @param vertex
   */
  public void addVertex(V vertex);

  /**
   * Returns the number of vertices.
   * 
   * @return
   */
  public int numVertices();

  /**
   * Returns all edges in this graph.
   * 
   * @return
   */
  public Set<E> getEdges();

  /**
   * Returns edges for the given vertex.
   * 
   * @param vertex
   * @return
   */
  public Set<E> getEdges(V vertex);
 
  /**
   * Adds the given edge that connects vertex 1 to vertex 2. The two vertices are also added if they
   * are not in this graph.
   * 
   * @param edge
   * @param vertex1
   * @param vertex2
   */
  public void addEdge(E edge, V vertex1, V vertex2);

  /**
   * Returns the number of edges.
   * 
   * @return
   */
  public int numEdges();

}
