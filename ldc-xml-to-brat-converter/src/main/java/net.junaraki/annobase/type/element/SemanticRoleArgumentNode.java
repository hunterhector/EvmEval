package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

public class SemanticRoleArgumentNode extends AbstractSemanticRoleNode {

  private static final long serialVersionUID = 890436923480226245L;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public SemanticRoleArgumentNode(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

}
