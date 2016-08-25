package net.junaraki.annobase.type.element;

import java.util.ArrayList;
import java.util.List;

import net.junaraki.annobase.AnnotationBase;
import net.junaraki.annobase.type.relation.element.SemanticRoleArgument;

public abstract class AbstractSemanticRoleNode extends TokenBasedTextSpan {

  private static final long serialVersionUID = -8890288098544800928L;

  protected List<SemanticRoleArgument> args;

  /**
   * Public constructor.
   * 
   * @param annBase
   * @param begin
   * @param end
   */
  public AbstractSemanticRoleNode(AnnotationBase annBase, int begin, int end) {
    super(annBase, begin, end);
    args = new ArrayList<SemanticRoleArgument>();
    setToken(null);
  }

  public List<SemanticRoleArgument> getArguments() {
    return args;
  }

  public void setArguments(List<SemanticRoleArgument> args) {
    this.args = args;
  }

  public void addArgument(SemanticRoleArgument arg) {
    args.add(arg);
  }

  public SemanticRoleArgumentNode getArgumentNode(String semanticRoleLabel) {
    for (SemanticRoleArgument arg : args) {
      if (semanticRoleLabel.equals(arg.getLabel())) {
        return (SemanticRoleArgumentNode) arg.getTo();
      }
    }
    return null;
  }

  public boolean hasArgument(String semanticRoleLabel) {
    for (SemanticRoleArgument arg : args) {
      if (semanticRoleLabel.equals(arg.getLabel())) {
        return true;
      }
    }
    return false;
  }

  /**
   * Returns the token associated with this semantic role node.
   * 
   * @return
   */
  public Token getToken() {
    return getFirstToken();
  }

  /**
   * Sets the associated token to this semantic role node.
   * 
   * @param token
   */
  public void setToken(Token token) {
    setFirstToken(token);
  }

}
