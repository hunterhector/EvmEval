package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

import net.junaraki.annobase.AnnotationBase;

public class ConstituencyNode extends TokenBasedTextSpan {

  private static final long serialVersionUID = -3956787187257745680L;

  private String label;

  private boolean isRoot;

  private boolean isLeaf;

  private ConstituencyNode parent;

  private List<ConstituencyNode> children;

  private Token token;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public ConstituencyNode(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    parent = null;
    children = new ArrayList<ConstituencyNode>();
  }

  public String getLabel() {
    return label;
  }

  public void setLabel(String label) {
    this.label = label;
  }

  public boolean isRoot() {
    return isRoot;
  }

  public void setRoot(boolean isRoot) {
    this.isRoot = isRoot;
  }

  public boolean isLeaf() {
    return isLeaf;
  }

  public void setLeaf(boolean isLeaf) {
    this.isLeaf = isLeaf;
  }

  public ConstituencyNode getParent() {
    return parent;
  }

  public void setParent(ConstituencyNode parent) {
    this.parent = parent;
  }

  public List<ConstituencyNode> getChildren() {
    return children;
  }

  public void setChildren(List<ConstituencyNode> children) {
    this.children = children;
  }

  /**
   * Finds the first child with the given label.
   * 
   * @param label
   * @return
   */
  public ConstituencyNode findChild(String label) {
    // Breadth-first search implementation
    Queue<ConstituencyNode> queue = new LinkedList<ConstituencyNode>();
    List<ConstituencyNode> visited = new ArrayList<ConstituencyNode>();

    queue.add(this);
    visited.add(this);

    while (!queue.isEmpty()) {
      ConstituencyNode currNode = queue.remove();
      if (currNode == null) {
        continue;
      }

      if (label.equals(currNode.getLabel())) {
        return currNode;
      }

      for (ConstituencyNode child : currNode.getChildren()) {
        if (child == null) {
          continue;
        }

        if (!visited.contains(child)) {
          queue.add(child);
          visited.add(child);
        }
      }
    }

    return null;
  }

  public Token getToken() {
    return token;
  }

  public void setToken(Token token) {
    this.token = token;
  }

}
