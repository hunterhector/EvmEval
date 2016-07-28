package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.DependencyNode;

public class DependencyRelation extends ElementDirectedBinaryRelation {

  private static final long serialVersionUID = -2920023035819088017L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public DependencyRelation(AnnotationBase annBase) {
    super(annBase);
  }

  public String getDependencyType() {
    return relationType;
  }

  public void setDependencyType(String dependencyType) {
    this.relationType = dependencyType;
  }

  public DependencyNode getHead() {
    return (DependencyNode) getFrom();
  }

  public void setHead(DependencyNode head) {
    setArg1(head);
  }

  public DependencyNode getChild() {
    return (DependencyNode) getTo();
  }

  public void setChild(DependencyNode child) {
    setArg2(child);
  }

}
