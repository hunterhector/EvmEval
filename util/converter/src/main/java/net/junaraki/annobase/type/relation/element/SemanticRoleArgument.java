package net.junaraki.annobase.type.relation.element;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.element.SemanticRoleArgumentNode;
import net.junaraki.annobase.type.element.SemanticRolePredicateNode;

public class SemanticRoleArgument extends ElementDirectedBinaryRelation {

  private static final long serialVersionUID = 440485693073097843L;

  /**
   * Public constructor.
   * 
   * @param annBase
   */
  public SemanticRoleArgument(AnnotationBase annBase) {
    super(annBase);
  }

  /**
   * Returns the semantic role label of this argument.
   * 
   * @return
   */
  public String getLabel() {
    return relationType;
  }

  /**
   * Sets the semantic role label to this argument.
   * 
   * @param label
   */
  public void setLabel(String label) {
    this.relationType = label;
  }

  public SemanticRolePredicateNode getPredicateNode() {
    return (SemanticRolePredicateNode) getFrom();
  }

  public void setPredicateNode(SemanticRolePredicateNode predNode) {
    setArg1(predNode);
  }

  public SemanticRoleArgumentNode getArgumentNode() {
    return (SemanticRoleArgumentNode) getTo();
  }

  public void setArgumentNode(SemanticRoleArgumentNode argNode) {
    setArg2(argNode);
  }

}
