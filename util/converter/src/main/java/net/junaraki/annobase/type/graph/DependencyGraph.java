package net.junaraki.annobase.type.graph;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.Annotation;
import net.junaraki.annobase.type.element.DependencyNode;
import net.junaraki.annobase.type.relation.element.DependencyRelation;
import net.junaraki.annobase.util.CollectionUtils;
import net.junaraki.annobase.util.graph.AbstractGraph;
import net.junaraki.annobase.util.graph.DijkstraShortestPath;

public class DependencyGraph extends AbstractGraph<DependencyNode, DependencyRelation> implements
        Annotation {

  private static final long serialVersionUID = -1201150383110251237L;

  private DependencyNode root;

  /** A document where this annotation is annotated */
  private final AnnotationBase annBase;

  /** The name of an annotation type. */
  private final String typeName;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public DependencyGraph(AnnotationBase annBase) {
    root = null;
    this.annBase = annBase;
    typeName = "DependencyGraph";
  }

  /**
   * Returns the shortest path from the given source node to the given destination node, using
   * Dijkstra's algorithm. This method returns the shortest path in terms of a list of dependency
   * nodes.
   * 
   * @param src
   * @param dest
   * @return
   */
  public List<DependencyNode> getDependencyPath(DependencyNode src, DependencyNode dest) {
    return DijkstraShortestPath.getShortestPath(this, src, dest);
  }

  /**
   * Returns the shortest path from the given source node to the given destination node, using
   * Dijkstra's algorithm. This method returns the shortest path in terms of a list of dependency
   * relations.
   * 
   * @param src
   * @param dest
   * @return
   */
  public List<DependencyRelation> getDependencyRelationPath(DependencyNode src, DependencyNode dest) {
    List<DependencyNode> depNodes = getDependencyPath(src, dest);

    List<DependencyRelation> depRels = new ArrayList<DependencyRelation>();
    for (int i = 0; i < depNodes.size() - 1; i++) {
      DependencyNode currNode = depNodes.get(i);
      DependencyNode nextNode = depNodes.get(i + 1);

      DependencyRelation headRel = currNode.getHeadRelation(nextNode);
      DependencyRelation childRel = currNode.getChildRelation(nextNode);
      if (headRel != null) {
        depRels.add(headRel);
      } else if (childRel != null) {
        depRels.add(childRel);
      } else {
        throw new RuntimeException("Unexpected error.");
      }
    }

    return depRels;
  }

  /**
   * Returns a string representing the shortest path from the given source node to the given
   * destination node, using Dijkstra's algorithm.
   * 
   * @param src
   * @param dest
   * @return
   */
  public String getDependencyPathString(DependencyNode src, DependencyNode dest) {
    List<DependencyNode> depNodes = getDependencyPath(src, dest);
    if (CollectionUtils.isEmpty(depNodes)) {
      // No dependency path found.
      return null;
    }

    StringBuilder depPath = new StringBuilder();
    for (int i = 0; i < depNodes.size() - 1; i++) {
      if (i > 0) {
        depPath.append("*");
      }

      DependencyNode currNode = depNodes.get(i);
      DependencyNode nextNode = depNodes.get(i + 1);

      DependencyRelation headRel = currNode.getHeadRelation(nextNode);
      DependencyRelation childRel = currNode.getChildRelation(nextNode);
      if (headRel != null) {
        depPath.append("<-");
        depPath.append(headRel.getDependencyType());
        depPath.append("--");
      } else if (childRel != null) {
        depPath.append("--");
        depPath.append(childRel.getDependencyType());
        depPath.append("->");
      } else {
        throw new RuntimeException("Unexpected error.");
      }
    }

    return depPath.toString();
  }

  /**
   * Returns a string representing the shortest path from the given source node to the given
   * destination node, using Dijkstra's algorithm.
   * 
   * @param src
   * @param srcStr
   * @param dest
   * @param destStr
   * @return
   */
  public String getDependencyPathString(DependencyNode src, String srcStr, DependencyNode dest,
          String destStr) {
    String depPath = getDependencyPathString(src, dest);
    if (depPath == null) {
      // No dependency path found.
      return null;
    }

    StringBuilder buf = new StringBuilder();
    buf.append(srcStr);
    buf.append(depPath);
    buf.append(destStr);
    return buf.toString();
  }

  @Override
  public String getTypeName() {
    return typeName;
  }

  @Override
  public AnnotationBase getAnnotationBase() {
    return annBase;
  }

  @Override
  public void addToBase() {
    annBase.addAnnotation(this);
  }

  @Override
  public void removeFromBase() {
    annBase.removeAnnotation(this);
  }

  @Override
  public Set<DependencyNode> getAdjacentVertices(DependencyNode depNode) {
    Set<DependencyNode> adjVertices = new HashSet<DependencyNode>();
    for (DependencyRelation depRel : getEdges(depNode)) {
      DependencyNode head = depRel.getHead();
      DependencyNode child = depRel.getChild();
      if (head.equals(depNode)) {
        adjVertices.add(child);
      } else if (child.equals(depNode)) {
        adjVertices.add(head);
      }
    }

    return adjVertices;
  }

  @Override
  public Set<DependencyRelation> getEdges(DependencyNode depNode) {
    Set<DependencyRelation> depRels = new HashSet<DependencyRelation>();
    depRels.addAll(depNode.getHeadRelations());
    depRels.addAll(depNode.getChildRelations());
    return depRels;
  }

  public DependencyNode getRoot() {
    return root;
  }

  public void setRoot(DependencyNode root) {
    this.root = root;
  }

}
