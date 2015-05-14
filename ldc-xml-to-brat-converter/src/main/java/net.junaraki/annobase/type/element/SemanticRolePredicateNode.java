package net.junaraki.annobase.type.element;

import net.junaraki.annobase.AnnotationBase;

/**
 * This class provides a node for semantic role labeling. A semantic role node is usually associated
 * with a single token.
 * 
 * @author Jun Araki
 */
public class SemanticRolePredicateNode extends AbstractSemanticRoleNode {

  private static final long serialVersionUID = -6058097929077228963L;

  private String rolesetId;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public SemanticRolePredicateNode(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
  }

  public String getRolesetId() {
    return rolesetId;
  }

  public void setRolesetId(String rolesetId) {
    this.rolesetId = rolesetId;
  }

}
