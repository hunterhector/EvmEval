package net.junaraki.annobase.util.graph;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;

public abstract class AbstractGraph<V, E> implements Graph<V, E>, Serializable {

  private static final long serialVersionUID = 8404124137395676120L;

  protected Set<V> vertices;

  protected Set<E> edges;

  /**
   * Public constructor.
   */
  public AbstractGraph() {
    vertices = new HashSet<V>();
    edges = new HashSet<E>();
  }

  /**
   * Returns all vertices in this graph.
   * 
   * @return
   */
  @Override
  public Set<V> getVertices() {
    return vertices;
  }

  /**
   * Returns vertices adjacent to the given vertex.
   * 
   * @param vertex
   * @return
   */
  public abstract Set<V> getAdjacentVertices(V vertex);

  /**
   * Adds the given vertex to this graph.
   * 
   * @param vertex
   */
  @Override
  public void addVertex(V vertex) {
    vertices.add(vertex);
  }

  /**
   * Returns the number of vertices.
   */
  @Override
  public int numVertices() {
    return vertices.size();
  }

  /**
   * Returns all edges in this graph.
   * 
   * @return
   */
  @Override
  public Set<E> getEdges() {
    return edges;
  }

  /**
   * Returns a collection of edges that the given vertex has.
   * 
   * @param vertex
   * @return
   */
  public abstract Set<E> getEdges(V vertex);

  /**
   * Adds the given edge that connects vertex 1 to vertex 2. The two vertices are also added if they
   * are not in this graph.
   * 
   * @param edge
   * @param vertex1
   * @param vertex2
   */
  @Override
  public void addEdge(E edge, V vertex1, V vertex2) {
    vertices.add(vertex1);
    vertices.add(vertex2);
    edges.add(edge);
  }

  /**
   * Returns the number of edges.
   */
  @Override
  public int numEdges() {
    return edges.size();
  }

}
