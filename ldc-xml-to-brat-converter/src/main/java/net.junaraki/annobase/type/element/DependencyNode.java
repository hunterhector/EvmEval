package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.relation.element.DependencyRelation;

/**
 * This class provides a node for dependency parsing. A dependency node is usually associated with a
 * single token.
 * 
 * @author Jun Araki
 */
public class DependencyNode extends TokenBasedTextSpan {

  private static final long serialVersionUID = 3172538746478421775L;

  private boolean isRoot;

  private List<DependencyRelation> headRelations;

  private List<DependencyRelation> childRelations;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public DependencyNode(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    headRelations = new ArrayList<DependencyRelation>();
    childRelations = new ArrayList<DependencyRelation>();
    setToken(null);
  }

  /**
   * Returns true if this node is an ancestor of the given node.
   * 
   * @param node
   * @return
   */
  public boolean isAncestor(DependencyNode node) {
    for (DependencyRelation headRel : node.getHeadRelations()) {
      DependencyNode head = headRel.getHead();
      if (head.equals(this)) {
        return true;
      } else {
        return isAncestor(head);
      }
    }

    return false;
  }

  public boolean isRoot() {
    return isRoot;
  }

  public void setRoot(boolean isRoot) {
    this.isRoot = isRoot;
  }

  public List<DependencyRelation> getHeadRelations() {
    return headRelations;
  }

  public void setHeadRelations(List<DependencyRelation> headRelations) {
    this.headRelations = headRelations;
  }

  public void addHeadRelation(DependencyRelation headRelation) {
    headRelations.add(headRelation);
  }

  /**
   * Returns a head relation if this dependency node has a head relation to the given node.
   * 
   * @param headNode
   * @return
   */
  public DependencyRelation getHeadRelation(DependencyNode headNode) {
    for (DependencyRelation headRelation : headRelations) {
      if (headRelation.getHead().equals(headNode)) {
        return headRelation;
      }
    }
    return null;
  }

  /**
   * Returns a head node if this dependency node has the given head dependency relation.
   * 
   * @param relationType
   * @return
   */
  public DependencyNode getHead(String relationType) {
    for (DependencyRelation headRelation : headRelations) {
      if (relationType.equals(headRelation.getRelationType())) {
        return headRelation.getHead();
      }
    }
    return null;
  }

  /**
   * Returns head nodes if this dependency node has the given head dependency relation.
   * 
   * @param relationType
   * @return
   */
  public List<DependencyNode> getHeads(String relationType) {
    List<DependencyNode> headNodes = new ArrayList<DependencyNode>();
    for (DependencyRelation headRelation : headRelations) {
      if (relationType.equals(headRelation.getRelationType())) {
        headNodes.add(headRelation.getHead());
      }
    }
    return headNodes;
  }

  /**
   * Returns true if this dependency node has a head dependency relation.
   * 
   * @return
   */
  public boolean hasHeadRelation() {
    return (headRelations.size() > 0);
  }

  /**
   * Returns true if this dependency node has the given head dependency relation.
   * 
   * @param relationType
   * @return
   */
  public boolean hasHeadRelation(String relationType) {
    for (DependencyRelation headRelation : headRelations) {
      if (relationType.equals(headRelation.getRelationType())) {
        return true;
      }
    }
    return false;
  }

  /**
   * Returns true if this dependency node has the given head dependency relation with the given
   * dependency node.
   * 
   * @param node
   * @param relationType
   * @return
   */
  public boolean hasHeadRelation(DependencyNode node, String relationType) {
    for (DependencyRelation headRelation : headRelations) {
      if (relationType.equals(headRelation.getRelationType())) {
        if (headRelation.getHead().equals(node)) {
          return true;
        }
      }
    }
    return false;
  }

  public List<DependencyRelation> getChildRelations() {
    return childRelations;
  }

  public void setChildRelations(List<DependencyRelation> childRelations) {
    this.childRelations = childRelations;
  }

  public void addChildRelation(DependencyRelation childRelation) {
    childRelations.add(childRelation);
  }

  /**
   * Returns a child relation if this dependency node has a child relation to the given node.
   * 
   * @param childNode
   * @return
   */
  public DependencyRelation getChildRelation(DependencyNode childNode) {
    for (DependencyRelation childRelation : childRelations) {
      if (childRelation.getChild().equals(childNode)) {
        return childRelation;
      }
    }
    return null;
  }

  /**
   * Returns a child node if this dependency node has the given child dependency relation.
   * 
   * @param relationType
   * @return
   */
  public DependencyNode getChild(String relationType) {
    for (DependencyRelation childRelation : childRelations) {
      if (relationType.equals(childRelation.getRelationType())) {
        return childRelation.getChild();
      }
    }
    return null;
  }

  /**
   * Returns child nodes if this dependency node has the given child dependency relation.
   * 
   * @param relationType
   * @return
   */
  public List<DependencyNode> getChildren(String relationType) {
    List<DependencyNode> childNodes = new ArrayList<DependencyNode>();
    for (DependencyRelation childRelation : childRelations) {
      if (relationType.equals(childRelation.getRelationType())) {
        childNodes.add(childRelation.getChild());
      }
    }
    return childNodes;
  }

  /**
   * Returns true if this dependency node has a child dependency relation.
   * 
   * @return
   */
  public boolean hasChildRelation() {
    return (childRelations.size() > 0);
  }

  /**
   * Returns true if this dependency node has the given child dependency relation.
   * 
   * @param relationType
   * @return
   */
  public boolean hasChildRelation(String relationType) {
    for (DependencyRelation childRelation : childRelations) {
      if (relationType.equals(childRelation.getRelationType())) {
        return true;
      }
    }
    return false;
  }

  /**
   * Returns true if this dependency node has the given child dependency relation with the given
   * dependency node.
   * 
   * @param node
   * @param relationType
   * @return
   */
  public boolean hasChildRelation(DependencyNode node, String relationType) {
    for (DependencyRelation childRelation : childRelations) {
      if (relationType.equals(childRelation.getRelationType())) {
        if (childRelation.getChild().equals(node)) {
          return true;
        }
      }
    }
    return false;
  }

  /**
   * Returns the token associated with this dependency node.
   * 
   * @return
   */
  public Token getToken() {
    return getFirstToken();
  }

  /**
   * Sets the associated token to this dependency node.
   * 
   * @param token
   */
  public void setToken(Token token) {
    setFirstToken(token);
  }

}
